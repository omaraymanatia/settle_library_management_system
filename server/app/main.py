from fastapi import FastAPI
from database.connection import engine, Base
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management System",
    description="A comprehensive library management system API",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to Library Management System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
