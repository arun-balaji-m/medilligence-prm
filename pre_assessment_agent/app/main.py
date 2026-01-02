# """
# Main FastAPI application for Pre-Assessment Agent
# """
#
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pre_assessment_agent.app.config import get_settings
# from pre_assessment_agent.app.routes import assessment_routes
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
#
#
#
# settings = get_settings()
#
# # Initialize FastAPI app
# app = FastAPI(
#     title=settings.APP_NAME,
#     version=settings.APP_VERSION,
#     description="AI-powered pre-assessment agent for collecting patient medical information"
# )
#
# app.mount("/static", StaticFiles(directory="static"), name="static")
#
# @app.get("/chat")
# async def chat_page():
#     return FileResponse("static/chat.html")
#
# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Include routers
# app.include_router(assessment_routes.router)
#
#
# @app.get("/")
# async def root():
#     """Root endpoint"""
#     return {
#         "message": "Pre-Assessment Agent API",
#         "version": settings.APP_VERSION,
#         "status": "active"
#     }
#
#
# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "environment": settings.ENVIRONMENT
#     }
#
#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True if settings.ENVIRONMENT == "development" else False
#     )


#
# """
# Main FastAPI application for Pre-Assessment Agent
# """
#
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from pathlib import Path
# from pre_assessment_agent.app.config import get_settings
# from pre_assessment_agent.app.routes import assessment_routes
#
# settings = get_settings()
#
# # Get the directory where main.py is located
# BASE_DIR = Path(__file__).resolve().parent
# STATIC_DIR = BASE_DIR / "static"
#
# # Initialize FastAPI app
# app = FastAPI(
#     title=settings.APP_NAME,
#     version=settings.APP_VERSION,
#     description="AI-powered pre-assessment agent for collecting patient medical information"
# )
#
# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Include routers
# app.include_router(assessment_routes.router)
#
# # Mount static files directory
# app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
#
#
# @app.get("/")
# async def root():
#     """Root endpoint"""
#     return {
#         "message": "Pre-Assessment Agent API",
#         "version": settings.APP_VERSION,
#         "status": "active"
#     }
#
#
# @app.get("/chat")
# async def chat_page():
#     """Serve the chat interface"""
#     chat_file = STATIC_DIR / "chat.html"
#     return FileResponse(chat_file)
#
#
# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "environment": settings.ENVIRONMENT
#     }
#
#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True if settings.ENVIRONMENT == "development" else False
#     )


"""
Main FastAPI application for Pre-Assessment Agent
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from pre_assessment_agent.app.config import get_settings
from pre_assessment_agent.app.routes import assessment_routes

settings = get_settings()

# Get the directory where main.py is located
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered pre-assessment agent for collecting patient medical information"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(assessment_routes.router)

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def chat_page():
    """Serve the chat interface"""
    chat_file = STATIC_DIR / "chat.html"
    return FileResponse(chat_file)


# async def root():
#     """Root endpoint"""
#     return {
#         "message": "Pre-Assessment Agent API",
#         "version": settings.APP_VERSION,
#         "status": "active"
#     }


# @app.get("/chat")
# async def chat_page():
#     """Serve the chat interface"""
#     chat_file = STATIC_DIR / "chat.html"
#     return FileResponse(chat_file)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )