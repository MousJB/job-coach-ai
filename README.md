# Job Coach AI — Backend

API FastAPI qui génère un CV réécrit et une lettre de motivation optimisés
pour une offre d'emploi donnée, via un pipeline de 9 étapes (extraction,
analyse, matching ATS, stratégie, réécriture, lettre, contrôle qualité).

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Créer un fichier `.env` à la racine :

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=qwen/qwen3-30b-a3b-thinking-2507

# Optionnel : modèles par palier (repli sur OPENROUTER_MODEL si absents)
OPENROUTER_MODEL_FAST=google/gemini-2.5-flash-lite
OPENROUTER_MODEL_QUALITY=

# Optionnel : origines CORS autorisées, séparées par des virgules
ALLOWED_ORIGINS=http://localhost:3000
```

> Le choix du modèle a un impact direct sur la latence perçue : un modèle
> "thinking"/raisonnement (ex: `qwen3-30b-a3b-thinking`) est nettement plus
> lent qu'un modèle standard. `OPENROUTER_MODEL_FAST` est utilisé pour les
> étapes factuelles (extraction, analyse, matching) et `OPENROUTER_MODEL_QUALITY`
> pour les étapes de rédaction (stratégie, réécriture CV, lettre, contrôle qualité).

## Lancer le serveur

```bash
python run.py
# ou : uvicorn app.main:app --reload
```

L'API est servie sur `http://127.0.0.1:8000`.

## Endpoints principaux

| Méthode | Route | Description |
|---|---|---|
| GET | `/health` | Health check léger (aucun appel LLM) |
| GET | `/ping-openrouter` | Health check coûteux (appel LLM réel) |
| POST | `/optimize` | Lance le pipeline complet, retourne le rapport final |
| POST | `/optimize/stream` | Variante streamée (SSE) : un événement par étape terminée |
| POST | `/export/cv-pdf` | Génère le PDF du CV (ReportLab) |
| POST | `/export/letter-pdf` | Génère le PDF de la lettre de motivation |

## Tests

```bash
pytest
```

Les tests mockent entièrement le client LLM (`app.services.llm_client.llm`) —
aucun appel réseau ni coût API pendant l'exécution de la suite.

## Architecture

- `app/pipeline/pipeline.py` — orchestrateur : exécute les étapes en respectant
  leurs vraies dépendances (extraction CV et analyse d'offre en parallèle),
  avec cache mémoire (TTL) sur les requêtes identiques.
- `app/services/llm_client.py` — client OpenRouter async, avec retry de
  réparation JSON et erreurs typées (`LLMUpstreamError`, `LLMResponseValidationError`).
- `app/services/pdf_service.py` — génération PDF pure Python (ReportLab, sans
  dépendance système).
- `app/prompts/*.md` — prompts système de chaque étape (français).
