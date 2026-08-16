#!/usr/bin/env python3
"""Wrapper de compatibilidade — redireciona para o pacote src/yt_downloader."""

import sys
from pathlib import Path

# Adicionar src/ ao path para que o pacote seja encontrado
sys.path.insert(0, str(Path(__file__).parent / "src"))

from yt_downloader.__main__ import main  # noqa: E402

if __name__ == "__main__":
    main()