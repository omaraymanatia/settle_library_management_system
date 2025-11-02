"""
Simple script to start the FastAPI server with correct module paths.
"""
import sys
import os

# Add the app directory to the Python path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[app_dir]
    )