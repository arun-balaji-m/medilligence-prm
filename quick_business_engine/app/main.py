# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from quick_business_engine.app.routes.assessment_routes import router as assessment_router
# from quick_business_engine.app.config import get_settings
# from quick_business_engine.app.utils.registry_setup import initialize_registry
# import uvicorn
# import os
#
# settings = get_settings()
#
# # Initialize FastAPI app
# app = FastAPI(
#     title="Quick Business Engine",
#     description="Natural Language to SQL Query Engine",
#     version="1.0.0"
# )
#
# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Mount static files
# static_path = os.path.join(os.path.dirname(__file__), "static")
# if os.path.exists(static_path):
#     app.mount("/static", StaticFiles(directory=static_path), name="static")
#
# # Include routers
# app.include_router(assessment_router)
#
#
# @app.get("/")
# async def root():
#     return FileResponse(os.path.join(static_path, "chat.html"))
#
#
# @app.on_event("startup")
# async def startup_event():
#     """Initialize services on startup"""
#     print("🚀 Quick Business Engine starting up...")
#     print(f"📊 ChromaDB directory: {settings.CHROMA_PERSIST_DIRECTORY}")
#
#     # Initialize registry on startup
#     print("🔧 Checking ChromaDB registry...")
#     registry_initialized = await initialize_registry()
#
#     if registry_initialized:
#         print("✅ Registry initialized successfully")
#     else:
#         print("ℹ️  Registry already exists")
#
#     print(f"🤖 Using models: Llama (Groq) + OpenAI GPT-4")
#     print("✅ Ready to process queries!")
#
#
# if __name__ == "__main__":
#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True
#     )

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from quick_business_engine.app.routes.assessment_routes import router as assessment_router
from quick_business_engine.app.config import get_settings
from quick_business_engine.app.utils.registry_setup import initialize_registry
import uvicorn
import os
import threading

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="Quick Business Engine",
    description="Natural Language to SQL Query Engine",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include routers
app.include_router(assessment_router)


@app.get("/")
async def root():
    return FileResponse(os.path.join(static_path, "chat.html"))


@app.on_event("startup")
def startup_event():
    print("🚀 Quick Business Engine starting up...")

    def background_init():
        print("🔧 Initializing ChromaDB registry...")
        initialize_registry()
        print("✅ Registry ready")

    threading.Thread(target=background_init, daemon=True).start()

    print("⚡ Server started, registry initializing in background")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )