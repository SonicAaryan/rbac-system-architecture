from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from app.config.database import get_db_connection

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload["user_id"]
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id, role FROM users WHERE id = %s AND token = %s", (user_id, token))
        user = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return {"id": user[0], "role": user[1]}
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
