from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
from jose import jwt
import jose
import os

SECRET_KEY = os.environ.get("SECRET_KEY") or "a super secret, secret key"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Look for the token in the Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
            
        if not token:
            return jsonify({'message': 'Token is missing!!'}), 404
        
        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['sub'] # Fetch user_id
            
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'message': 'Invalid'}), 401
        
        return f(user_id, *args, **kwargs)
    
    return decorated

def encode_token(user_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1), # Setting the expiration time to an hour past now
        'iat': datetime.now(timezone.utc), # Issued At
        'sub': str(user_id) # This needs to be a string ore the token will be malformed and won't be able to be decoded
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    return token