"""Funções utilitárias e configuração de logging."""

from datetime import datetime
from pathlib import Path
import logging
import os
import re
import subprocess
import sys
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging() -> logging.Logger:
    """Configura e retorna o logger da aplicação."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"yt_downloader_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger("yt_downloader")


logger = setup_logging()


# ---------------------------------------------------------------------------
# URL / texto
# ---------------------------------------------------------------------------

def limpar_url(raw_url: str) -> str:
    """Extrai e limpa uma URL de várias representações (markdown, angle brackets, etc)."""
    url = (raw_url or "").strip()
    if not url:
        return ""

    if url.startswith("<") and url.endswith(">"):
        url = url[1:-1].strip()

    match = re.search(r"https?://\S+", url)
    if match:
        return match.group(0).rstrip(")")

    if url.startswith("[") and "](" in url and url.endswith(")"):
        return url.split("](", 1)[1][:-1].strip()

    return url


def sanitizar_nome(nome: str) -> str:
    """Remove caracteres ilegais de nomes de arquivo."""
    nome = (nome or "playlist").strip()
    nome = re.sub(r'[<>:"/\\|?*\x00-\x1F]+', "_", nome)
    nome = nome.rstrip(". ")
    return nome or "playlist"


def validar_url_youtube(url: str) -> bool:
    """Valida se a URL é do YouTube."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if parsed.scheme not in {"http", "https"}:
        return False

    host = parsed.netloc.lower().replace("www.", "")
    youtube_hosts = {"youtube.com", "m.youtube.com", "youtu.be"}

    if host in youtube_hosts:
        return True
    if host.endswith(".youtube.com"):
        return True
    return False


def obter_tempo_formatado() -> str:
    """Retorna a hora atual formatada para uso em nomes de arquivo."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def abrir_pasta(caminho: Path) -> None:
    """Abre a pasta no explorador de arquivos do sistema."""
    try:
        if sys.platform == "win32":
            os.startfile(caminho)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", caminho])
        else:
            subprocess.Popen(["xdg-open", caminho])
        logger.info("Pasta aberta: %s", caminho)
    except (OSError, FileNotFoundError) as e:
        logger.error("Erro ao abrir pasta: %s", e)
