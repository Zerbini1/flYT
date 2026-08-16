"""Backend de download — classe YoutubeDownloader."""

from pathlib import Path
import shutil

import yt_dlp
from yt_dlp.utils import DownloadError

from .constants import QUALIDADES, FORMATOS, PlaylistGrandeError
from .utils import (
    logger,
    validar_url_youtube,
    sanitizar_nome,
    obter_tempo_formatado,
    abrir_pasta,
)


class YoutubeDownloader:
    """Classe principal para gerenciar downloads do YouTube."""

    def __init__(self):
        self.pasta_downloads = Path("downloads")
        self.pasta_downloads.mkdir(parents=True, exist_ok=True)
        self.archive_path = self.pasta_downloads / ".yt-dlp-archive.txt"
        self.ffmpeg_instalado = shutil.which("ffmpeg") is not None
        self.cancelar = False

    def resetar_historico(self) -> None:
        """Reseta o histórico de downloads."""
        if self.archive_path.exists():
            self.archive_path.unlink()
            logger.info("Histórico de downloads resetado")

    def obter_pasta_categoria(self, categoria: str) -> Path:
        """Cria e retorna pasta por categoria."""
        pasta = self.pasta_downloads / categoria
        pasta.mkdir(parents=True, exist_ok=True)
        return pasta

    def baixar_url(
        self,
        url: str,
        eh_playlist: bool,
        qualidade: str,
        formato: str,
        categoria: str = "Geral",
        renomear_com_data: bool = True,
        callback_progresso=None,
        confirmar_playlist_grande: bool = False,
    ) -> bool:
        """Baixa vídeo ou playlist com as opções configuradas."""

        if not validar_url_youtube(url):
            mensagem = "URL inválida. Use um link do YouTube (youtube.com ou youtu.be)."
            logger.error(mensagem)
            return False

        try:
            # Determinar pasta de destino
            if categoria and categoria != "Geral":
                pasta_destino = self.obter_pasta_categoria(categoria)
            else:
                pasta_destino = self.pasta_downloads

            # Configurar formato de saída com data/hora se solicitado
            if renomear_com_data:
                if eh_playlist:
                    outtmpl = str(pasta_destino / f"%(title)s_{obter_tempo_formatado()}.%(ext)s")
                else:
                    outtmpl = str(pasta_destino / f"%(title)s_{obter_tempo_formatado()}.%(ext)s")
            else:
                outtmpl = str(pasta_destino / "%(title)s.%(ext)s")

            # Validar se é playlist e pedir confirmação
            if eh_playlist:
                with yt_dlp.YoutubeDL({"extract_flat": True, "skip_download": True, "quiet": True}) as ydl:
                    info = ydl.extract_info(url, download=False)

                num_videos = 0
                if isinstance(info, dict):
                    if "entries" in info:
                        num_videos = len(info["entries"])

                    playlist_title = info.get("title", "playlist")
                    if categoria and categoria != "Geral":
                        pasta_playlist = pasta_destino / sanitizar_nome(playlist_title)
                    else:
                        pasta_playlist = self.pasta_downloads / sanitizar_nome(playlist_title)
                    pasta_playlist.mkdir(parents=True, exist_ok=True)
                    # Para playlists, usamos o índice para manter a ordem e evitar duplicatas (ignoramos renomear_com_data)
                    outtmpl = str(pasta_playlist / "%(playlist_index)s - %(title)s.%(ext)s")

                # Pedir confirmação se playlist grande
                if num_videos > 10 and not confirmar_playlist_grande:
                    raise PlaylistGrandeError(num_videos, url)

            # Configurar opções do yt-dlp
            opcoes = {
                "format": QUALIDADES.get(qualidade, QUALIDADES["Melhor (automático)"]),
                "merge_output_format": FORMATOS.get(formato, "mp4"),
                "download_archive": str(self.archive_path),
                "noplaylist": not eh_playlist,
                "outtmpl": outtmpl,
                "quiet": False,
                "no_warnings": False,
            }

            if qualidade == "Somente Áudio":
                opcoes["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]

            if callback_progresso:
                opcoes["progress_hooks"] = [callback_progresso]

            logger.info("Iniciando download: %s", url)
            logger.info("Qualidade: %s, Formato: %s, Categoria: %s", qualidade, formato, categoria)

            with yt_dlp.YoutubeDL(opcoes) as ydl:
                ydl.download([url])

            logger.info("Download concluído com sucesso: %s", url)

            # Abrir pasta de destino
            if categoria and categoria != "Geral":
                abrir_pasta(pasta_destino)
            else:
                abrir_pasta(self.pasta_downloads)

            return True

        except PlaylistGrandeError:
            raise  # Propagar para a GUI tratar
        except DownloadError as erro:
            logger.error("Erro no download: %s", erro)
            return False
        except (OSError, IOError, ValueError) as erro:
            logger.error("Erro inesperado: %s", erro)
            return False
