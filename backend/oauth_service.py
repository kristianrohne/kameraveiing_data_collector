# oauth_service.py
import os
import requests
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import current_app
from urllib.parse import urlencode

class AnimaliaOAuthService:
    def __init__(self):
        self.client_id = os.getenv('ANIMALIA_CLIENT_ID')
        self.client_secret = os.getenv('ANIMALIA_CLIENT_SECRET')
        
        # Use correct Animalia SSO endpoints
        self.environment = os.getenv('ANIMALIA_ENVIRONMENT', 'staging')  # 'staging' or 'production'
        if self.environment == 'production':
            self.auth_url = 'https://sso.animalia.no/authorize'
            self.token_url = 'https://sso.animalia.no/token'
            self.keys_url = 'https://sso.animalia.no/keys'
            self.logout_url = 'https://sso.animalia.no/logout'
        else:
            self.auth_url = 'https://staging-sso.animalia.no/authorize'
            self.token_url = 'https://staging-sso.animalia.no/token'
            self.keys_url = 'https://staging-sso.animalia.no/keys'
            self.logout_url = 'https://staging-sso.animalia.no/logout'
            
        self.redirect_uri = os.getenv('ANIMALIA_REDIRECT_URI', 'http://172.17.250.225:8000/api/auth/oauth/callback')
        print(f"🔧 OAuth Service initialized with redirect_uri: {self.redirect_uri}")
        
    def get_authorization_url(self, state: str = None) -> str:
        """Generate the authorization URL to redirect users to Animalia SSO"""
        params = {
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'auto_login': 'true',
            'scope': 'openid profile email offline_access pid'
        }
        
        if state:
            params['state'] = state
            
        # Use proper URL encoding
        param_string = urlencode(params)
        full_url = f"{self.auth_url}?{param_string}"
        
        # Debug logging
        print(f"🔗 Generated OAuth URL: {full_url}")
        print(f"📍 Redirect URI: {self.redirect_uri}")
        
        return full_url
    
    def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token using Animalia's specification"""
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'redirect_uri': self.redirect_uri
        }
        
        headers = {
            'Accept': 'application/json'
        }
        
        response = requests.post(self.token_url, data=data, headers=headers)
        
        if response.status_code != 201:  # Animalia returns 201 Created on success
            raise Exception(f"Token exchange failed: {response.text}")
            
        return response.json()
    
    def verify_access_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode the Animalia access token using their public keys"""
        try:
            # Get the key ID from the token header
            unverified_header = jwt.get_unverified_header(access_token)
            kid = unverified_header.get('kid')
            
            if not kid:
                return None
                
            # Fetch public keys directly
            headers = {'Accept': 'application/json'}
            response = requests.get(self.keys_url, headers=headers)
            
            if response.status_code != 200:
                return None
                
            keys = response.json().get('keys', [])
            
            # Find the matching key
            public_key = None
            for key in keys:
                if key.get('kid') == kid:
                    # Convert JWK to PEM format for PyJWT
                    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                    break
                    
            if not public_key:
                return None
                
            # Verify and decode the token
            decoded = jwt.decode(
                access_token, 
                public_key, 
                algorithms=['RS256'],
                options={"verify_exp": True}
            )
            
            return decoded
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            print(f"Token verification error: {e}")
            return None
    
    def get_user_info_from_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Fetch user information from Animalia SSO /userinfo endpoint using the access token"""
        # Use the correct userinfo endpoint for staging/production
        if self.environment == 'production':
            userinfo_url = 'https://sso.animalia.no/userinfo'
        else:
            userinfo_url = 'https://staging-sso.animalia.no/userinfo'

        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(userinfo_url, headers=headers)
            print(f"🔍 Userinfo endpoint response status: {response.status_code}")
            print(f"🔍 Userinfo endpoint response body: {response.text}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to fetch userinfo: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Exception while fetching userinfo: {e}")
            return None

    def get_logout_url(self, redirect_uri: str = None) -> str:
        """Generate logout URL for Animalia SSO"""
        if redirect_uri:
            return f"{self.logout_url}?redirect_uri={redirect_uri}"
        return self.logout_url

# Global instance
oauth_service = AnimaliaOAuthService()
