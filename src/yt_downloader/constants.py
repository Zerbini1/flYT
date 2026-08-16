"""Constantes e exceções do YouTube Downloader."""


# Mapeamento de qualidades
QUALIDADES = {
    "Melhor (automático)": "bestvideo+bestaudio/best",
    "4K (2160p)": "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=2160]+bestaudio/best",
    "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best",
    "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best",
    "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best",
    "Somente Áudio": "bestaudio[ext=m4a]/bestaudio",
}

FORMATOS = {
    "MP4": "mp4",
    "MKV": "mkv",
    "WebM": "webm",
}


class PlaylistGrandeError(Exception):
    """Levantada quando uma playlist excede o limite de vídeos sem confirmação."""

    def __init__(self, num_videos: int, url: str):
        self.num_videos = num_videos
        self.url = url
        super().__init__(f"Playlist com {num_videos} vídeos requer confirmação.")
