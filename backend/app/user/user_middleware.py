from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from app.config.database import get_db_connection,release_db_connection

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "access")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Security(oauth2_scheme)):
    try:
        print("Decoding token:", token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload["user_id"]
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            print("Querying user with id:", user_id)  # Debugging
            cur.execute("SELECT id, role, token FROM users WHERE id = %s AND token = %s", (user_id, token))
            user = cur.fetchone()
            
            if not user:
                print("User not found or token mismatch")  # Debugging
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            return {"id": user[0], "role": user[1], "token": user[2]}  # Include token in return value
        finally:
            cur.close()
            release_db_connection(conn)
    
    except JWTError as e:
        print("JWT Error:", e)  # Debugging
        raise HTTPException(status_code=401, detail="Invalid token")