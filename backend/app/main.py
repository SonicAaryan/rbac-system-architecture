from fastapi import FastAPI
# from app.config.database import get_db_connection
from app.config.database import init_db_pool, close_db_pool
from app.user.user_route import router as user_router

app = FastAPI(title="RBAC System with FastAPI")

# Include User Routes

# Check database connection at startup
# @app.on_event("startup")
# def startup_event():
#     count=0
#     conn = get_db_connection()
#     if conn:
#         print("✅ Connected to Database Successfully","---->",count++1)
#     else:
#         print("❌ Database Connection Failed")
#     # Closing connection immediately (to avoid unintentional open connections)
#     if conn:
#         conn.close()

@app.on_event("startup")
def startup_event():
    """Initialize database connection pool on app startup."""
    init_db_pool()

@app.on_event("shutdown")
def shutdown_event():
    """Close the database connection pool on app shutdown."""
    close_db_pool()

app.include_router(user_router, prefix="/user", tags=["User"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the RBAC system!"}
