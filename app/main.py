from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
 
from app.routes import profile, listings, chat, users
from app.services.scheduler import start_scheduler
 
load_dotenv()
 
app = FastAPI(title="Scanline API")
 
# Allows your Vercel-hosted frontend to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your real frontend URL once you have one
    allow_methods=["*"],
    allow_headers=["*"],
)
 
app.include_router(users.router)
app.include_router(profile.router)
app.include_router(listings.router)
app.include_router(chat.router)
 
 
@app.on_event("startup")
def on_startup():
    start_scheduler()
 
 
@app.get("/health")
def health():
    return {"status": "ok"}
 
