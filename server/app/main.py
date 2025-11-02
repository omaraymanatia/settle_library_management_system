from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from db.session import engine, Base
from api.user import router as user_router
from api.auth import router as auth_router
from api.book import router as book_router
from api.reservation import router as reservation_router
from api.payment import router as payment_router
from api.borrow import router as borrow_router
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management System",
    description="A comprehensive library management system API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(book_router, prefix="/api/v1")
app.include_router(reservation_router, prefix="/api/v1")
app.include_router(payment_router, prefix="/api/v1")
app.include_router(borrow_router, prefix="/api/v1/borrows", tags=["borrows"])

@app.get("/")
async def root():
    return {"message": "Welcome to Library Management System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 404 handler for all unmatched routes
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested endpoint '{request.url.path}' was not found",
            "status_code": 404,
            "path": request.url.path
        }
    )

# Catch-all route for any unmatched paths (this should be the last route)
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def catch_all(request: Request, path: str):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested endpoint '/{path}' was not found",
            "status_code": 404,
            "path": f"/{path}",
            "method": request.method
        }
    )
