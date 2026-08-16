"""Entry point — python -m yt_downloader."""

from .cli import parse_args, run_cli


def main() -> None:
    """Função principal: decide entre GUI e CLI."""
    args = parse_args()

    # CLI com --reset-archive (sem URL) — executar e sair
    if args.reset_archive and not args.url and not args.cli:
        from .core import YoutubeDownloader
        from .utils import logger

        downloader = YoutubeDownloader()
        downloader.resetar_historico()
        logger.info("Histórico de downloads resetado.")
        return

    # Modo CLI
    if args.cli:
        run_cli(args)
        return

    # Modo GUI (padrão)
    import ttkbootstrap as ttk
    from .gui import YoutubeDownloaderGUI

    root = ttk.Window(
        themename="darkly",
        title="flYT",
        size=(960, 740),
        resizable=(True, True),
        minsize=(860, 680),
    )
    YoutubeDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
