from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.optimize import router as optimize_router

app = FastAPI(title="Job Coach API")

# Configuration CORS (pour autoriser ton frontend à appeler cette API plus tard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, tu mettras l'URL de ton front ici
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routes
app.include_router(health_router)
app.include_router(optimize_router)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Job Coach API is running 🚀"
    }