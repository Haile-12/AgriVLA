from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import colorama
from colorama import Fore, Style, Back

from app.config.settings import settings
from app.persistence.mongodb.connection import connect_to_mongo, close_mongo_connection
from app.knowledge.retrieval import get_rag_retriever
from app.api.routes import auth, agents

# Initialize colorama
colorama.init(autoreset=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} Connecting to MongoDB...")
    await connect_to_mongo()
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Connected to MongoDB successfully.")
    
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} Initializing Qdrant RAG Retriever...")
    get_rag_retriever()
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Qdrant initialized successfully.")
    
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} AgriVLA is ready to receive requests.")
    yield
    print(f"\n{Fore.YELLOW}[WARN]{Style.RESET_ALL} Shutting down AgriVLA Server...")
    await close_mongo_connection()
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Database connections closed.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Closed-Loop Vision-Language Agent API",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(agents.router)

@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}

@app.get("/ready", tags=["system"])
async def readiness_check():
    from app.persistence.mongodb.connection import get_database
    db = get_database()
    if db is not None:
        try:
            await db.command("ping")
            return {"status": "ready", "database": "connected"}
        except Exception:
            return {"status": "not_ready", "database": "disconnected"}
    return {"status": "not_ready", "database": "not_initialized"}
