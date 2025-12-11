from fastapi import Header, HTTPException, Depends
from google.oauth2 import id_token
from google.auth.transport import requests
import os

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')  # strict validation

def verify_google_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail='Missing Authorization header')

    token = authorization.replace("Bearer", "").strip()

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # Always return consistent structure
        return {
            "user_id": idinfo["sub"],
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
        }

    except Exception as e:
        print("Google token verification failed:", e)
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(user = Depends(verify_google_token)):
    return user["user_id"]   # clean and guaranteed now
