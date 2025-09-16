# app.py
import os, uuid
from flask import Flask, jsonify, request, send_from_directory, redirect, session
from flask_cors import CORS
from dotenv import load_dotenv
from models import init_db, SessionLocal, Upload, User
from storage import save_image, UPLOAD_ROOT
from auth import (
    create_jwt_token, verify_jwt_token, 
    get_user_by_id, get_user_by_farmer_id, get_user_by_email, create_user_from_oauth
)
from oauth_service import oauth_service
import secrets
from functools import wraps

load_dotenv()

# Validate critical environment variables
REQUIRED_ENV_VARS = [
    "ANIMALIA_CLIENT_ID", 
    "ANIMALIA_CLIENT_SECRET", 
    "JWT_SECRET"
]

missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    print(f"❌ Missing required environment variables: {missing_vars}")
    print("Please check your .env file")

# Safe logging of configuration (mask secrets)
def mask_secret(value, show_chars=4):
    """Mask secret values for safe logging"""
    if not value or len(value) <= show_chars:
        return "***"
    return value[:show_chars] + "*" * (len(value) - show_chars)

print("🔐 OAuth Configuration:")
print(f"   Client ID: {mask_secret(os.getenv('ANIMALIA_CLIENT_ID'))}")
print(f"   Client Secret: {mask_secret(os.getenv('ANIMALIA_CLIENT_SECRET'))}")
print(f"   Environment: {os.getenv('ANIMALIA_ENVIRONMENT', 'staging')}")


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB cap
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(32))
# Flask-Session config
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "/home/kristian/kameraveiing_data_collector/backend/flask_session"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_KEY_PREFIX"] = "kameraveiing:"
# Cookie settings for cross-domain (ngrok/frontend)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
from flask_session import Session
Session(app)

# CORS configuration to support credentials (sessions + JWT)
CORS(app, resources={r"/*": {"origins": ["http://localhost:4200", "http://172.17.250.225:4200", "http://172.17.250.146:4200"]}}, supports_credentials=True)

init_db()

def get_current_user():
    """Get current user from JWT token, OAuth token, or session (backward compatibility)"""
    # Check for JWT token in Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # First try JWT token (existing users)
        payload = verify_jwt_token(token)
        if payload:
            user = get_user_by_id(payload['user_id'])
            if user:
                return user
        
        # Then try OAuth token (Animalia SSO)
        user_info = oauth_service.get_user_info_from_token(token)
        if user_info:
            # Find or create user based on OAuth info
            user = get_user_by_farmer_id(user_info.get('farmer_id')) or get_user_by_id(user_info.get('id'))
            if user:
                return user
            # Auto-create user from OAuth if they don't exist
            return None
    
    return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return {"error": "Authentication required"}, 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# UPLOAD ENDPOINTS
# ============================================================================
# Dummy /api/auth/me endpoint for frontend authentication check
from flask import jsonify


# Real OAuth login endpoint for Animalia SSO
@app.route("/api/auth/oauth/login", methods=['GET'])
def oauth_login():
    try:
        # Generate a random state for CSRF protection
        import secrets
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        print(f"🎲 Generated state: {state}")
        print("Set session oauth_state:", session.get('oauth_state'))
        auth_url = oauth_service.get_authorization_url(state=state)
        print(f"🎯 Generated auth URL: {auth_url}")
        return {"auth_url": auth_url}
    except Exception as e:
        print(f"❌ OAuth login failed: {str(e)}")
        return {"error": f"OAuth login failed: {str(e)}"}, 500
    
@app.route("/api/auth/me", methods=['GET'])
def auth_me():
    """Get current user info from JWT token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return {"error": "No token provided"}, 401
    
    token = auth_header.split(' ')[1]
    
    try:
        import jwt
        # Decode the JWT token to get user info
        payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        
        return jsonify({
            "user": {
                "user_id": payload.get('user_id'),
                "email": payload.get('email'),
                "name": payload.get('name'),
                "farmer_id": payload.get('farmer_id'),
                "authenticated": True
            }
        })
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}, 401
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}, 401

@app.route("/api/upload", methods=['POST'])
def create_upload():
    """Upload pig photo (authenticated)"""
    if "image" not in request.files:
        return {"error": "missing image"}, 400
    image = request.files["image"]
    filename = image.filename

    # Parse info from filename: weight_uid_picnum_date_timestamp_device.png
    # Example: 61.00kg_uid0606_46_20250606_103744319_iOS.png
    import re
    match = re.match(r"([\d.]+)kg_([^_]+)_([\d]+)_([\d]{8})_([\d]+)_([^_.]+)\.png", filename)
    if match:
        weight = match.group(1)
        uid = match.group(2)
        picture_number = match.group(3)
        date = match.group(4)
        timestamp = match.group(5)
        filename = image.filename
        weight = request.form.get("weight")
        # Generate date and timestamp at upload time
        from datetime import datetime
        now = datetime.now()
        date = now.strftime("%Y%m%d")
        timestamp = now.strftime("%H%M%S%f")
        # Get uploader info from session/auth (dummy fallback if not available)
        user = None
        try:
            user = get_current_user()
        except Exception:
            pass
        uploader = user.full_name if user and hasattr(user, "full_name") else (user.user_id if user and hasattr(user, "user_id") else "unknown")

        # Save image to dummy S3
        import os
        s3_dir = os.path.join(os.path.dirname(__file__), "dummy_s3")
        os.makedirs(s3_dir, exist_ok=True)
        image.save(os.path.join(s3_dir, filename))

        # Save tabular data to dummy Azure SQL (CSV file)
        import csv
        csv_path = os.path.join(os.path.dirname(__file__), "dummy_azure_sql.csv")
        header = ["filename", "weight", "date", "timestamp", "uploader"]
        file_exists = os.path.isfile(csv_path)
        need_header = True
        if file_exists:
            with open(csv_path, "r") as f:
                first_line = f.readline().strip()
                if first_line == ",".join(header):
                    need_header = False

        with open(csv_path, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if need_header:
                writer.writerow(header)
            writer.writerow([filename, weight, date, timestamp, uploader])

        return {
            "status": "ok",
            "filename": filename,
            "weight": weight,
            "date": date,
            "timestamp": timestamp,
            "uploader": uploader
        }, 201

# OAuth callback endpoint
@app.route("/api/auth/oauth/callback", methods=['GET'])
def oauth_callback():
    """Handle OAuth callback from Animalia SSO"""
    try:
        state = request.args.get('state')
        if not state or 'oauth_state' not in session or state != session['oauth_state']:
            print(f"❌ State verification failed")
            return {"error": "Invalid state parameter"}, 400
        
        # Clean up state from session
        session.pop('oauth_state', None)
        
        # Get authorization code
        code = request.args.get('code')
        if not code:
            error = request.args.get('error')
            print(f"❌ No authorization code. Error: {error}")
            return {"error": f"OAuth error: {error or 'No authorization code'}"}, 400
        
        print(f"✅ Authorization code received: {code[:10]}...")
        
        # Exchange code for token
        token_response = oauth_service.exchange_code_for_token(code)
        print(f"🔑 Token response: {token_response}")
        id_token = token_response.get('id_token')
        print(f"🔑 id_token: {id_token}")
        if not id_token:
            print("❌ No id_token in token response!")
            return {"error": "Failed to get id_token"}, 400

        # Decode id_token for minimal user info
        import jwt
        try:
            decoded = jwt.decode(id_token, options={"verify_signature": False})
            print(f"🔍 Decoded id_token: {decoded}")
        except Exception as e:
            print(f"❌ Failed to decode id_token: {e}")
            return {"error": "Failed to decode id_token"}, 400

        # Minimal user check: only allow users with a valid 'email' and 'pid' (farmer_id)
        email = decoded.get('email')
        farmer_id = decoded.get('pid')
        name = decoded.get('name', '')
        user_id = decoded.get('sub')
        
        if not email or not farmer_id:
            print("❌ Missing required user info in id_token")
            return {"error": "Unauthorized: missing required user info"}, 403

        print(f"✅ User authenticated: {name} ({email}) - Farmer ID: {farmer_id}")
        
        # Create a simple JWT token with just the SSO data (no database needed)
        import jwt
        from datetime import datetime, timedelta
        
        # Create a simple token with user info
        token_payload = {
            'user_id': str(user_id),
            'email': email,
            'name': name,
            'farmer_id': str(farmer_id),
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        jwt_token = jwt.encode(token_payload, 'your-secret-key', algorithm='HS256')

        # For web clients, redirect to frontend with token
        frontend_url = os.getenv('FRONTEND_URL', 'http://172.17.250.225:4200')
        redirect_url = f"{frontend_url}/auth/callback?token={jwt_token}"
        print(f"🎯 Redirecting to: {redirect_url}")
        return redirect(redirect_url)

    except Exception as e:
        return {"error": f"OAuth callback failed: {str(e)}"}, 500

@app.route("/api/auth/logout", methods=['POST'])
def logout():
    """Logout with optional SSO logout"""
    try:
        data = request.get_json() or {}
        include_sso_logout = data.get('sso_logout', True)  # Default to True for complete logout
        
        if include_sso_logout:
            # Generate SSO logout URL that redirects back to our login page
            frontend_url = os.getenv('FRONTEND_URL', 'http://172.17.250.225:4200')
            logout_redirect = f"{frontend_url}/login"
            sso_logout_url = oauth_service.get_logout_url(logout_redirect)
            
            return {
                "message": "Logout successful",
                "sso_logout_url": sso_logout_url,
                "redirect_to_sso": True
            }
        else:
            # Just local logout
            return {"message": "Local logout successful"}
            
    except Exception as e:
        return {"error": f"Logout failed: {str(e)}"}, 500

# ============================================================================
# UPLOAD ENDPOINTS
# ============================================================================
# CORE ENDPOINTS (Protected)
# ============================================================================

@app.route("/api/health", methods=['GET'])
def health():
    return {"ok": True}

@app.route("/api/user", methods=['GET'])
@require_auth
def get_user():
    """Get current user information"""
    user = request.current_user
    return {"user_id": user.farmer_id, "authenticated": True, "full_name": user.full_name}

    # ...existing code...
    
    # If no pig_uid provided, generate a new one based on timestamp and user
    if not pig_uid:
        import time
        pig_uid = f"{user.farmer_id}_{int(time.time())}"

    db = SessionLocal()
    try:
        # Get the next picture number for this pig from this user
        last_upload = db.query(Upload).filter(
            Upload.pig_uid == pig_uid,
            Upload.user_id == user.farmer_id
        ).order_by(Upload.picture_number.desc()).first()
        picture_number = (last_upload.picture_number + 1) if last_upload else 1
        
        rel_path, _ = save_image(image, weight, pig_uid, picture_number, user.farmer_id)
        
        u = Upload(
            id=str(uuid.uuid4()), 
            pig_uid=pig_uid,
            user_id=user.farmer_id,
            picture_number=picture_number,
            filename=rel_path, 
            weight_kg=weight
        )
        db.add(u)
        db.commit()
        
        return {
            "id": u.id, 
            "pig_uid": u.pig_uid,
            "user_id": u.user_id,
            "picture_number": u.picture_number,
            "image_url": f"/files/{rel_path}", 
            "weight": u.weight_kg
        }, 201
    except ValueError as e:
        return {"error": str(e)}, 400
    finally:
        db.close()

@app.route("/api/uploads", methods=['GET'])
@require_auth
def list_uploads():
    """Get uploads for the current user only"""
    user = request.current_user
    db = SessionLocal()
    try:
        rows = db.query(Upload).filter(
            Upload.user_id == user.farmer_id
        ).order_by(Upload.created_at.desc()).limit(100).all()
    finally:
        db.close()
    
    return jsonify([
        {
            "id": r.id, 
            "pig_uid": r.pig_uid,
            "user_id": r.user_id,
            "picture_number": r.picture_number,
            "image_url": f"/files/{r.filename}", 
            "weight": r.weight_kg, 
            "created_at": r.created_at.isoformat()
        }
        for r in rows
    ])

@app.route("/api/pigs", methods=['GET'])
@require_auth
def list_pigs():
    """Get all pigs for the current user with their picture counts"""
    user = request.current_user
    db = SessionLocal()
    try:
        from sqlalchemy import func
        pig_data = db.query(
            Upload.pig_uid,
            Upload.user_id,
            Upload.weight_kg,
            func.count(Upload.id).label('picture_count'),
            func.max(Upload.created_at).label('latest_upload')
        ).filter(
            Upload.user_id == user.farmer_id
        ).group_by(Upload.pig_uid, Upload.user_id, Upload.weight_kg).all()
        
        return jsonify([
            {
                "pig_uid": row.pig_uid,
                "user_id": row.user_id,
                "weight": row.weight_kg,
                "picture_count": row.picture_count,
                "latest_upload": row.latest_upload.isoformat()
            }
            for row in pig_data
        ])
    finally:
        db.close()

# serve images (dev-only)
@app.route("/files/<path:rel>", methods=['GET'])
def files(rel):
    safe_root = os.path.abspath(UPLOAD_ROOT)
    return send_from_directory(safe_root, rel, as_attachment=False)

if __name__ == "__main__":
    os.makedirs("data/uploads", exist_ok=True)
    app.run(host="0.0.0.0", port=int(os.getenv("APP_PORT", "8000")), debug=True)