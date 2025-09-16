from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
from flask_session import Session
import os
import secrets
from datetime import datetime
import pandas as pd

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB cap for large image files
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(32))
# Flask-Session config
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = os.path.join(os.path.dirname(__file__), "flask_session")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True

# Initialize extensions
CORS(app, origins=["http://localhost:4200"], supports_credentials=True)
Session(app)

# Simple user simulation (since we lost the models)
USERS = {}

def get_current_user():
    """Get current user (simplified)"""
    user_id = session.get("user_id")
    if user_id and user_id in USERS:
        return USERS[user_id]
    return None

# AUTH ENDPOINTS

@app.get("/api/auth/oauth/login")
def oauth_login():
    """Initiate OAuth login (simplified)"""
    try:
        # Generate a simple state
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        
        # Simplified OAuth URL for Animalia SSO
        client_id = os.getenv('ANIMALIA_CLIENT_ID', 'ingris-datainnsamling')
        redirect_uri = "http://localhost:8000/api/auth/callback"
        auth_url = f"https://staging-sso.animalia.no/authorize?redirect_uri={redirect_uri}&client_id={client_id}&auto_login=true&scope=openid+profile+email+offline_access+pid&state={state}"
        
        return {"auth_url": auth_url}, 200
    except Exception as e:
        print(f"❌ OAuth login failed: {str(e)}")
        return {"error": f"OAuth login failed: {str(e)}"}, 500

@app.get("/api/auth/me")
def get_me():
    """Get current user info"""
    user = get_current_user()
    if not user:
        return {"error": "Not authenticated"}, 401
    
    return user, 200

@app.get("/api/auth/callback")
def oauth_callback():
    """Handle OAuth callback (simplified)"""
    try:
        state = request.args.get("state")
        if not state or 'oauth_state' not in session or state != session['oauth_state']:
            return {"error": "Invalid state parameter"}, 400
        
        code = request.args.get("code")
        if not code:
            return {"error": "Missing authorization code"}, 400
        
        # Simplified user creation
        user_id = "test-user-" + secrets.token_hex(8)
        user = {
            "user_id": user_id,
            "farmer_id": "farmer-123",
            "full_name": "Test User",
            "email": "test@example.com"
        }
        
        USERS[user_id] = user
        session["user_id"] = user_id
        
        # Redirect to frontend
        frontend_callback_url = f"http://localhost:4200/auth/callback?success=true"
        return redirect(frontend_callback_url)
        
    except Exception as e:
        print(f"❌ OAuth callback failed: {str(e)}")
        return {"error": f"OAuth callback failed: {str(e)}"}, 500

# UPLOAD ENDPOINTS

@app.post("/api/upload")
def create_upload():
    """Upload pig photo"""
    if "image" not in request.files:
        return {"error": "missing image"}, 400
    
    image = request.files["image"]
    filename = image.filename
    weight = request.form.get("weight")
    
    # Get uploader info
    user = get_current_user()
    uploader = user.get("full_name", "unknown") if user else "unknown"

    # Save image to dummy S3
    s3_dir = os.path.join(os.path.dirname(__file__), "dummy_s3")
    os.makedirs(s3_dir, exist_ok=True)
    image.save(os.path.join(s3_dir, filename))

    # Save tabular data to CSV
    csv_path = os.path.join(os.path.dirname(__file__), "dummy_azure_sql.csv")
    
    columns = [
        "id", "filename", "weight_kg", "upload_date", 
        "upload_time", "uploader_name", "created_at"
    ]
    
    now = datetime.now()
    upload_date = now.strftime("%Y-%m-%d")
    upload_time = now.strftime("%H:%M:%S")
    
    # Check if CSV exists
    if not os.path.exists(csv_path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(csv_path, index=False)
    
    # Read existing data
    df = pd.read_csv(csv_path)
    
    # Generate new ID
    new_id = 1 if df.empty else df["id"].max() + 1
    
    # Create new record
    new_row = {
        "id": new_id,
        "filename": filename,
        "weight_kg": float(weight) if weight else None,
        "upload_date": upload_date,
        "upload_time": upload_time, 
        "uploader_name": uploader,
        "created_at": now.isoformat()
    }
    
    # Append to dataframe
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(csv_path, index=False)
    
    return {
        "status": "ok",
        "id": new_id,
        "filename": filename,
        "weight_kg": float(weight) if weight else None,
        "upload_date": upload_date,
        "upload_time": upload_time, 
        "uploader_name": uploader,
        "created_at": now.isoformat()
    }, 201

@app.get("/api/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)