"""Modo CLI — parsing de argumentos e execução via linha de comando."""

import argparse
import sys

from .constants import QUALIDADES, FORMATOS
from .core import YoutubeDownloader
from .utils import limpar_url, logger


def parse_args(argv=None) -> argparse.Namespace:
    """Configura e retorna os argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="flYT — Downloader de YouTube com interface gráfica avançada",
    )
    parser.add_argument("--cli", action="store_true", help="Modo linha de comando (sem GUI)")
    parser.add_argument("url", nargs="?", help="URL do vídeo ou playlist")
    parser.add_argument("--playlist", action="store_true", help="Baixar como playlist")
    parser.add_argument(
        "--quality",
        choices=list(QUALIDADES.keys()),
        default="Melhor (automático)",
        help="Qualidade do vídeo",
    )
    parser.add_argument(
        "--format",
        choices=list(FORMATOS.keys()),
        default="MP4",
        help="Formato de saída",
    )
    parser.add_argument("--category", default="Geral", help="Categoria de download")
    parser.add_argument(
        "--reset-archive",
        action="store_true",
        help="Resetar histórico de downloads",
    )
    return parser.parse_args(argv)


def run_cli(args: argparse.Namespace) -> None:
    """Executa o download via CLI."""
    downloader = YoutubeDownloader()

    if args.reset_archive:
        downloader.resetar_historico()
        logger.info("Histórico de downloads resetado.")

    if not args.url:
        logger.error("Nenhuma URL fornecida.")
        sys.exit(1)

    url = limpar_url(args.url)
    if not url:
        logger.error("URL inválida.")
        sys.exit(1)

    sucesso = downloader.baixar_url(
        url=url,
        eh_playlist=args.playlist,
        qualidade=args.quality,
        formato=args.format,
        categoria=args.category,
    )
    sys.exit(0 if sucesso else 1)
