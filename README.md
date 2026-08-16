# flYT

Downloader de vídeos e playlists do YouTube com interface gráfica profissional e modo CLI.

## Funcionalidades

- **Download de vídeo único ou playlist** com seleção de qualidade (4K → 480p + áudio)
- **Download em lote** — cole várias URLs de uma vez
- **Organização automática** por categorias (subpastas em `downloads/`)
- **Barra de progresso real** com velocidade e ETA
- **Prevenção de duplicatas** via histórico de downloads
- **Modo CLI** completo para automação e scripts

## Pré-requisitos

- **Python 3.10+**
- **ffmpeg** (para merge de vídeo+áudio e conversão)

```bash
# Windows
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

## Instalação

```bash
git clone <repo-url> && cd yt-download
pip install -r requirements.txt
```

## Uso

### Interface gráfica (padrão)

```bash
python yt.py
```

### Linha de comando

```bash
# Vídeo em melhor qualidade
python yt.py --cli "https://www.youtube.com/watch?v=VIDEO_ID"

# Vídeo em 1080p, formato MKV, na categoria "Tutoriais"
python yt.py --cli "https://www.youtube.com/watch?v=VIDEO_ID" \
    --quality "1080p" --format MKV --category "Tutoriais"

# Playlist inteira em 720p
python yt.py --cli "https://www.youtube.com/playlist?list=PLAYLIST_ID" \
    --playlist --quality "720p"

# Somente áudio (MP3)
python yt.py --cli "https://www.youtube.com/watch?v=VIDEO_ID" \
    --quality "Somente Áudio"

# Resetar histórico de downloads
python yt.py --cli --reset-archive
```

### Opções CLI

| Flag | Descrição |
|---|---|
| `--cli` | Ativa modo linha de comando |
| `--playlist` | Trata a URL como playlist |
| `--quality` | `Melhor (automático)`, `4K (2160p)`, `1080p`, `720p`, `480p`, `Somente Áudio` |
| `--format` | `MP4`, `MKV`, `WebM` |
| `--category` | Nome da subpasta em `downloads/` (padrão: `Geral`) |
| `--reset-archive` | Apaga o histórico de vídeos já baixados |

## Estrutura do projeto

```
yt-download/
├── src/yt_downloader/       # Pacote principal
│   ├── __init__.py          # Versão e metadados
│   ├── __main__.py          # Entry point
│   ├── constants.py         # Qualidades, formatos, exceções
│   ├── utils.py             # Utilitários e logging
│   ├── core.py              # YoutubeDownloader (backend)
│   ├── gui.py               # YoutubeDownloaderGUI (ttkbootstrap)
│   └── cli.py               # Parsing de argumentos e execução CLI
├── docs/
│   └── CHANGELOG.md         # Histórico de versões
├── yt.py                    # Wrapper de compatibilidade
├── requirements.txt
├── .gitignore
└── README.md
```

### Pastas de runtime (criadas automaticamente)

- `downloads/` — vídeos baixados, organizados por categoria
- `logs/` — um arquivo de log por sessão

## Troubleshooting

| Problema | Solução |
|---|---|
| "ffmpeg não encontrado" | Instale o ffmpeg (veja Pré-requisitos acima) |
| "URL inválida" | Use apenas links do YouTube: `youtube.com/watch?v=...` ou `youtu.be/...` |
| Download falha silenciosamente | Verifique os logs em `logs/` e se o vídeo não é privado/removido |
| Vídeo já baixado é ignorado | Use "Resetar Histórico" para limpar o registro de duplicatas |

## Dependências

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — engine de download
- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) — tema visual da GUI
