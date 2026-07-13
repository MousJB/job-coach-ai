import logging
import logging.handlers
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent.parent / "logs" / "pipeline"


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure le logging applicatif : console + fichier tournant.

    Ne journalise jamais le contenu brut des CV/offres (vie privée) — les
    steps du pipeline ne loggent que des identifiants d'étape et des durées.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "app.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    # Ces librairies sont très bavardes en INFO/DEBUG, on les tait.
    for noisy_logger in ("httpx", "httpcore", "openai"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)
