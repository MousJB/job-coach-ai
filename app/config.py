from dotenv import load_dotenv
import os

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")

# Modèles optionnels par palier (repli sur OPENROUTER_MODEL si absents).
# Permet d'utiliser un modèle rapide/économique pour les étapes d'extraction
# et de réserver un modèle plus capable aux étapes de rédaction/jugement.
OPENROUTER_MODEL_FAST = os.getenv("OPENROUTER_MODEL_FAST") or None
OPENROUTER_MODEL_QUALITY = os.getenv("OPENROUTER_MODEL_QUALITY") or None

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY manquante")

if not OPENROUTER_MODEL:
    raise ValueError("OPENROUTER_MODEL manquante")

_DEFAULT_ALLOWED_ORIGINS = [
    "https://job-coach-frontend-theta.vercel.app",
    "http://localhost:3000",
]

_allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = (
    [origin.strip() for origin in _allowed_origins_env.split(",") if origin.strip()]
    or _DEFAULT_ALLOWED_ORIGINS
)
