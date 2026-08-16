"""Interface gráfica — YoutubeDownloaderGUI (ttkbootstrap darkly)."""

from datetime import datetime
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

from yt_dlp.utils import DownloadError

from .constants import QUALIDADES, FORMATOS, PlaylistGrandeError
from .core import YoutubeDownloader
from .utils import limpar_url, abrir_pasta


class YoutubeDownloaderGUI:
    """Interface gráfica para o YouTube Downloader — v3.0.0 (ttkbootstrap darkly)."""

    def __init__(self, root):
        self.root = root
        self.downloader = YoutubeDownloader()
        self.root.title("flYT")
        self.root.geometry("960x740")
        self.root.resizable(True, True)
        self.root.minsize(860, 680)

        # Aplicar cor escura na barra de título do Windows
        import sys
        if sys.platform == "win32":
            try:
                import pywinstyles
                pywinstyles.change_header_color(self.root, color="#222222")
            except ImportError:
                pass

        # Centralizar janela na tela
        self._center_window()

        # Variável de progresso
        self._progress_var = tk.DoubleVar(value=0)
        self._progress_label_var = tk.StringVar(value="")
        self._downloading = False

        self.setup_ui()
        self.url_em_lote = []

    def _center_window(self):
        """Centraliza a janela na tela."""
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def setup_ui(self):
        """Configura a interface gráfica com ttkbootstrap."""
        import ttkbootstrap as ttk
        from ttkbootstrap.constants import SUCCESS, DANGER, PRIMARY, INFO, SECONDARY

        # ========== HEADER ==========
        header_frame = ttk.Frame(self.root, bootstyle="dark")
        header_frame.pack(fill=tk.X)

        header_inner = ttk.Frame(header_frame, bootstyle="dark")
        header_inner.pack(fill=tk.X, padx=20, pady=(16, 12))

        ttk.Label(
            header_inner,
            text="flYT",
            font=("Segoe UI", 20, "bold"),
            bootstyle="inverse-dark",
        ).pack(side=tk.LEFT)

        ttk.Label(
            header_inner,
            text="v3.0  ·  Download de vídeos com qualidade",
            font=("Segoe UI", 10),
            bootstyle="secondary-inverse",
        ).pack(side=tk.LEFT, padx=(16, 0), pady=(4, 0))

        ttk.Separator(self.root).pack(fill=tk.X)

        # ========== FFMPEG WARNING BANNER ==========
        if not self.downloader.ffmpeg_instalado:
            warn_frame = ttk.Frame(self.root, bootstyle="warning")
            warn_frame.pack(fill=tk.X, padx=0, pady=0)

            ttk.Label(
                warn_frame,
                text=(
                    "⚠  ffmpeg não encontrado — conversão de áudio e merge de qualidade podem falhar.  "
                    "Instale: choco install ffmpeg (Windows) / brew install ffmpeg (macOS) / apt install ffmpeg (Linux)"
                ),
                font=("Segoe UI", 9),
                bootstyle="inverse-warning",
                wraplength=900,
            ).pack(padx=16, pady=8)

        # ========== CONTEÚDO PRINCIPAL ==========
        main_frame = ttk.Frame(self.root, padding=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- URL ---
        ttk.Label(main_frame, text="URL do Vídeo ou Playlist", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 4))
        url_frame = ttk.Frame(main_frame, padding=12, bootstyle="dark")
        url_frame.pack(fill=tk.X, pady=(0, 16))

        self.url_entry = ttk.Entry(url_frame, font=("Segoe UI", 10))
        self.url_entry.pack(fill=tk.X, ipady=4)
        
        # Placeholder logica
        self.url_entry.insert(0, "Cole o link do YouTube aqui...")
        self.url_entry.configure(foreground="gray")

        def on_url_focus_in(event):
            if self.url_entry.get() == "Cole o link do YouTube aqui...":
                self.url_entry.delete(0, tk.END)
                self.url_entry.configure(foreground="white")

        def on_url_focus_out(event):
            if not self.url_entry.get().strip():
                self.url_entry.insert(0, "Cole o link do YouTube aqui...")
                self.url_entry.configure(foreground="gray")

        self.url_entry.bind("<FocusIn>", on_url_focus_in)
        self.url_entry.bind("<FocusOut>", on_url_focus_out)

        # --- OPÇÕES ---
        ttk.Label(main_frame, text="OPÇÕES DE DOWNLOAD", font=("Segoe UI", 10, "bold"), foreground="#888888").pack(anchor=tk.W, pady=(8, 8))
        opts_frame = ttk.Frame(main_frame)
        opts_frame.pack(fill=tk.X, pady=(0, 16))

        # Configurar 4 colunas com peso igual
        opts_frame.columnconfigure(0, weight=1, uniform="opts")
        opts_frame.columnconfigure(1, weight=1, uniform="opts")
        opts_frame.columnconfigure(2, weight=1, uniform="opts")
        opts_frame.columnconfigure(3, weight=1, uniform="opts")

        # Labels (Cabeçalhos das colunas)
        ttk.Label(opts_frame, text="Tipo de Conteúdo", font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W, pady=(0, 4), padx=(0, 10))
        ttk.Label(opts_frame, text="Qualidade Desejada", font=("Segoe UI", 9)).grid(row=0, column=1, sticky=tk.W, pady=(0, 4), padx=(0, 10))
        ttk.Label(opts_frame, text="Formato do Arquivo", font=("Segoe UI", 9)).grid(row=0, column=2, sticky=tk.W, pady=(0, 4), padx=(0, 10))
        ttk.Label(opts_frame, text="Pasta / Categoria", font=("Segoe UI", 9)).grid(row=0, column=3, sticky=tk.W, pady=(0, 4), padx=(0, 10))

        # Coluna 0: Tipo
        self.tipo_var = tk.StringVar(value="video")
        tipo_inner = ttk.Frame(opts_frame)
        tipo_inner.grid(row=1, column=0, sticky=tk.EW, padx=(0, 10))
        ttk.Radiobutton(tipo_inner, text="Vídeo", variable=self.tipo_var, value="video", bootstyle="success-toolbutton").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Radiobutton(tipo_inner, text="Playlist", variable=self.tipo_var, value="playlist", bootstyle="success-toolbutton").pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Coluna 1: Qualidade
        self.qualidade_var = tk.StringVar(value="Melhor (automático)")
        ttk.Combobox(
            opts_frame, textvariable=self.qualidade_var,
            values=list(QUALIDADES.keys()), state="readonly"
        ).grid(row=1, column=1, sticky=tk.EW, padx=(0, 10), ipady=3)

        # Coluna 2: Formato
        self.formato_var = tk.StringVar(value="MP4")
        ttk.Combobox(
            opts_frame, textvariable=self.formato_var,
            values=list(FORMATOS.keys()), state="readonly"
        ).grid(row=1, column=2, sticky=tk.EW, padx=(0, 10), ipady=3)

        # Coluna 3: Categoria
        self.categoria_var = tk.StringVar(value="Geral")
        self.categoria_entry = ttk.Entry(opts_frame, textvariable=self.categoria_var)
        self.categoria_entry.grid(row=1, column=3, sticky=tk.EW, padx=(0, 10), ipady=3)

        # Linha inferior (Renomear) - Span 4 colunas
        bottom_opts_frame = ttk.Frame(main_frame)
        bottom_opts_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.renomear_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            bottom_opts_frame, text="Renomear arquivo adicionando data/hora do download",
            variable=self.renomear_var, bootstyle="success-square-toggle",
        ).pack(side=tk.LEFT)
        
        ttk.Label(bottom_opts_frame, text="Destino: /downloads/flYT/", font=("Segoe UI", 9), foreground="#888888").pack(side=tk.RIGHT)

        # --- BOTÕES ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(4, 8))

        # Ação primária — cor base
        ttk.Button(
            btn_frame, text="▶  Baixar",
            command=self.baixar_video,
            bootstyle=SUCCESS, width=16,
        ).pack(side=tk.LEFT, padx=(0, 6))

        # Ações secundárias
        ttk.Button(
            btn_frame, text="Baixar Playlist",
            command=self.baixar_playlist,
            bootstyle=f"{SUCCESS}-outline", width=16,
        ).pack(side=tk.LEFT, padx=(0, 6))

        ttk.Button(
            btn_frame, text="Baixar em Lote",
            command=self.abrir_lote,
            bootstyle=f"{SUCCESS}-outline", width=16,
        ).pack(side=tk.LEFT, padx=(0, 6))

        ttk.Button(
            btn_frame, text="Abrir Pasta",
            command=self.abrir_pasta_destino,
            bootstyle=SECONDARY, width=14,
        ).pack(side=tk.LEFT, padx=(0, 6))

        # Ação destrutiva — Ghost button isolado à direita
        ttk.Button(
            btn_frame, text="Resetar Histórico",
            command=self.resetar_historico,
            bootstyle="danger-link", width=18, cursor="hand2"
        ).pack(side=tk.RIGHT)

        # --- PROGRESSO ---
        ttk.Label(main_frame, text="Status", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(8, 4))
        status_frame = ttk.Frame(main_frame, padding=12, bootstyle="dark")
        status_frame.pack(fill=tk.BOTH, expand=True)

        # Label de progresso
        prog_top = ttk.Frame(status_frame)
        prog_top.pack(fill=tk.X, pady=(0, 4))

        self.progress_label = ttk.Label(
            prog_top, textvariable=self._progress_label_var,
            font=("Segoe UI", 9),
        )
        self.progress_label.pack(side=tk.LEFT)

        self.progress_pct = ttk.Label(
            prog_top, text="",
            font=("Segoe UI", 9, "bold"),
        )
        self.progress_pct.pack(side=tk.RIGHT)

        # Barra de progresso — elemento de assinatura
        self.progress = ttk.Progressbar(
            status_frame,
            variable=self._progress_var,
            maximum=100,
            mode="determinate",
            bootstyle="success-striped",
            length=400,
        )
        self.progress.pack(fill=tk.X, pady=(0, 8))

        # Log
        log_frame = ttk.Frame(status_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)

        # Determinar cores de fundo do tema atual
        style = ttk.Style.get_instance()
        bg_color = style.colors.inputbg
        fg_color = style.colors.inputfg

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            state=tk.DISABLED,
            bg=bg_color,
            fg=fg_color,
            insertbackground=style.colors.primary,
            selectbackground=style.colors.selectbg,
            font=("Consolas", 10),
            relief=tk.FLAT,
            borderwidth=1,
            wrap=tk.WORD,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Tags de cor para o log
        self.log_text.tag_configure("normal", foreground=fg_color)
        self.log_text.tag_configure("dim", foreground="#888888")
        
        # Tags de Badges
        self.log_text.tag_configure("info_badge", foreground=style.colors.info, font=("Consolas", 10, "bold"))
        self.log_text.tag_configure("success_badge", foreground=style.colors.success, font=("Consolas", 10, "bold"))
        self.log_text.tag_configure("warning_badge", foreground=style.colors.warning, font=("Consolas", 10, "bold"))
        self.log_text.tag_configure("error_badge", foreground=style.colors.danger, font=("Consolas", 10, "bold"))

        # Mensagem de boas-vindas
        self._log_welcome()

    # ------------------------------------------------------------------
    # Log
    # ------------------------------------------------------------------

    def _log_welcome(self):
        """Exibe mensagem inicial no log."""
        self.log_message("Sistema flYT v3.0 inicializado e pronto para uso.", "INFO")
        self.log_message('Cole uma URL do YouTube acima e clique em "Baixar".', "INFO")
        if not self.downloader.ffmpeg_instalado:
            self.log_message(
                "ffmpeg não encontrado — conversões de áudio podem falhar.",
                "WARNING",
            )

    def log_message(self, message: str, level: str = "NORMAL"):
        """Escreve mensagem no log visual com badges."""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")

        tag = level.lower()
        if tag not in ("normal", "success", "warning", "error"):
            # Auto detect based on message content
            msg_lower = message.lower()
            if "erro" in msg_lower or "falha" in msg_lower or "error" in msg_lower:
                tag = "error"
            elif "aviso" in msg_lower or "atenção" in msg_lower or "warning" in msg_lower:
                tag = "warning"
            elif "sucesso" in msg_lower or "concluído" in msg_lower:
                tag = "success"
            else:
                tag = "info"

        badge_text = ""
        badge_tag = ""
        if tag == "success":
            badge_text = " SUCESSO "
            badge_tag = "success_badge"
        elif tag == "error":
            badge_text = " ERRO "
            badge_tag = "error_badge"
        elif tag == "warning":
            badge_text = " AVISO "
            badge_tag = "warning_badge"
        else:
            badge_text = " INFO "
            badge_tag = "info_badge"

        self.log_text.insert(tk.END, f"[{timestamp}]", "dim")
        self.log_text.insert(tk.END, badge_text, badge_tag)
        self.log_text.insert(tk.END, f"{message}\n", "normal")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    # ------------------------------------------------------------------
    # Progress hook
    # ------------------------------------------------------------------

    def _progress_hook(self, d: dict):
        """Callback do yt-dlp — atualiza barra de progresso via root.after()."""
        status = d.get("status", "")

        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)

            if total > 0:
                pct = min((downloaded / total) * 100, 100)
                speed = d.get("_speed_str", "").strip()
                eta = d.get("_eta_str", "").strip()
                info = f"Baixando... {speed}  ETA {eta}" if speed else "Baixando..."
                self.root.after(0, self._update_progress, pct, info)
            else:
                self.root.after(0, self._update_progress, -1, "Baixando...")

        elif status == "finished":
            self.root.after(0, self._update_progress, 100, "Processando...")

    def _update_progress(self, pct: float, text: str):
        """Atualiza a barra e label de progresso (thread-safe, chamado via root.after)."""
        if pct < 0:
            if self.progress.cget("mode") != "indeterminate":
                self.progress.configure(mode="indeterminate")
                self.progress.start(15)
            self._progress_label_var.set(text)
            self.progress_pct.configure(text="")
        else:
            if self.progress.cget("mode") != "determinate":
                self.progress.stop()
                self.progress.configure(mode="determinate")
            self._progress_var.set(pct)
            self._progress_label_var.set(text)
            self.progress_pct.configure(text=f"{pct:.0f}%")

    def _reset_progress(self):
        """Reseta a barra de progresso ao estado inicial."""
        self.progress.stop()
        self.progress.configure(mode="determinate")
        self._progress_var.set(0)
        self._progress_label_var.set("")
        self.progress_pct.configure(text="")
        self._downloading = False

    # ------------------------------------------------------------------
    # Ações de download
    # ------------------------------------------------------------------

    def baixar_video(self):
        """Baixa um vídeo único."""
        url = limpar_url(self.url_entry.get())
        if not url:
            messagebox.showerror("Erro", "Por favor, insira uma URL.")
            return

        if self._downloading:
            messagebox.showwarning("Aguarde", "Um download já está em andamento.")
            return

        self._downloading = True
        self._update_progress(0, "Iniciando download...")
        self.log_message(f"Iniciando download: {url}")

        threading.Thread(
            target=self._executar_download,
            args=(url, False),
            daemon=True,
        ).start()

    def baixar_playlist(self):
        """Baixa uma playlist."""
        url = limpar_url(self.url_entry.get())
        if not url:
            messagebox.showerror("Erro", "Por favor, insira uma URL.")
            return

        if self._downloading:
            messagebox.showwarning("Aguarde", "Um download já está em andamento.")
            return

        self._downloading = True
        self._update_progress(0, "Analisando playlist...")
        self.log_message(f"Iniciando download de playlist: {url}")

        threading.Thread(
            target=self._executar_download,
            args=(url, True),
            daemon=True,
        ).start()

    def _executar_download(self, url: str, eh_playlist: bool, confirmar_grande: bool = False):
        """Executa o download em thread separada."""
        aguardando_confirmacao = False
        try:
            sucesso = self.downloader.baixar_url(
                url=url,
                eh_playlist=eh_playlist,
                qualidade=self.qualidade_var.get(),
                formato=self.formato_var.get(),
                categoria=self.categoria_var.get(),
                renomear_com_data=self.renomear_var.get(),
                callback_progresso=self._progress_hook,
                confirmar_playlist_grande=confirmar_grande,
            )

            if sucesso:
                self.root.after(0, self._update_progress, 100, "Concluído!")
                self.root.after(0, self.log_message, "Download concluído com sucesso!", "SUCCESS")
                self.root.after(0, messagebox.showinfo, "Sucesso", "Download concluído com sucesso!")
            else:
                self.root.after(0, self.log_message, "Falha no download. Verifique a URL e as opções.", "ERROR")
                self.root.after(0, messagebox.showerror, "Erro", "Falha no download. Verifique o log para detalhes.")

        except PlaylistGrandeError as e:
            aguardando_confirmacao = True

            def _ask_confirm():
                resp = messagebox.askyesno(
                    "Playlist Grande",
                    f"Esta playlist contém {e.num_videos} vídeos.\n\n"
                    f"Deseja continuar o download de todos?",
                )
                if resp:
                    self.log_message(f"Usuário confirmou download de playlist com {e.num_videos} vídeos.", "INFO")
                    threading.Thread(
                        target=self._executar_download,
                        args=(url, True, True),
                        daemon=True,
                    ).start()
                else:
                    self.log_message("Download de playlist cancelado pelo usuário.", "WARNING")
                    self._reset_progress()

            self.root.after(0, _ask_confirm)

        except (OSError, IOError, DownloadError) as e:
            self.root.after(0, self.log_message, f"Erro: {e}", "ERROR")
            self.root.after(0, messagebox.showerror, "Erro", f"Erro: {e}")
        finally:
            if not aguardando_confirmacao:
                self.root.after(500, self._reset_progress)

    def resetar_historico(self):
        """Reseta o histórico de downloads."""
        if messagebox.askyesno(
            "Resetar Histórico",
            "Isso apagará o registro de vídeos já baixados.\n"
            "Downloads futuros poderão re-baixar vídeos anteriores.\n\n"
            "Tem certeza?",
        ):
            self.downloader.resetar_historico()
            self.log_message("Histórico de downloads resetado.", "WARNING")
            messagebox.showinfo("Sucesso", "Histórico resetado!")

    def abrir_pasta_destino(self):
        """Abre a pasta de downloads."""
        abrir_pasta(self.downloader.pasta_downloads)

    # ------------------------------------------------------------------
    # Download em lote
    # ------------------------------------------------------------------

    def abrir_lote(self):
        """Abre interface para download em lote."""
        import ttkbootstrap as ttk
        from ttkbootstrap.constants import SUCCESS, SECONDARY

        lote_window = tk.Toplevel(self.root)
        lote_window.title("Baixar em Lote")
        lote_window.geometry("640x460")
        lote_window.transient(self.root)
        lote_window.grab_set()

        # Header do lote
        header = ttk.Frame(lote_window, padding=(16, 12))
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Insira as URLs (uma por linha):",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor=tk.W)

        ttk.Label(
            header,
            text="Cada URL será baixada como vídeo individual com as opções da tela principal.",
            font=("Segoe UI", 9),
            bootstyle="secondary",
        ).pack(anchor=tk.W, pady=(2, 0))

        # Área de texto
        txt_frame = ttk.Frame(lote_window, padding=(16, 0, 16, 0))
        txt_frame.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style.get_instance()

        urls_text = scrolledtext.ScrolledText(
            txt_frame, height=15,
            font=("Consolas", 10),
            bg=style.colors.inputbg,
            fg=style.colors.inputfg,
            insertbackground=style.colors.primary,
            relief=tk.FLAT,
            borderwidth=1,
            wrap=tk.WORD,
        )
        urls_text.pack(fill=tk.BOTH, expand=True)

        # Botões
        btn_frame = ttk.Frame(lote_window, padding=16)
        btn_frame.pack(fill=tk.X)

        status_lbl = ttk.Label(btn_frame, text="", font=("Segoe UI", 9))
        status_lbl.pack(side=tk.LEFT)

        ttk.Button(
            btn_frame, text="Cancelar",
            command=lote_window.destroy,
            bootstyle=f"{SECONDARY}-outline", width=12,
        ).pack(side=tk.RIGHT, padx=(6, 0))

        def processar_lote():
            urls = urls_text.get("1.0", tk.END).strip().split("\n")
            urls = [limpar_url(u) for u in urls if limpar_url(u)]

            if not urls:
                messagebox.showerror("Erro", "Nenhuma URL válida encontrada.", parent=lote_window)
                return

            self.log_message(f"Iniciando download em lote: {len(urls)} URLs", "INFO")
            processar_btn.configure(state=tk.DISABLED)

            def _run_batch():
                sucesso_count = 0
                falha_count = 0

                for i, url in enumerate(urls, 1):
                    self.root.after(0, status_lbl.configure, {"text": f"Baixando {i}/{len(urls)}..."})
                    self.root.after(0, self.log_message, f"[Lote {i}/{len(urls)}] Baixando: {url}", "INFO")

                    ok = self.downloader.baixar_url(
                        url=url,
                        eh_playlist=False,
                        qualidade=self.qualidade_var.get(),
                        formato=self.formato_var.get(),
                        categoria=self.categoria_var.get(),
                        renomear_com_data=self.renomear_var.get(),
                        callback_progresso=self._progress_hook,
                    )

                    if ok:
                        sucesso_count += 1
                        self.root.after(0, self.log_message, f"[Lote {i}/{len(urls)}] Concluído!", "SUCCESS")
                    else:
                        falha_count += 1
                        self.root.after(0, self.log_message, f"[Lote {i}/{len(urls)}] Falhou: {url}", "ERROR")

                resumo = f"Lote finalizado: {sucesso_count} OK, {falha_count} falha(s) de {len(urls)} URLs."
                self.root.after(0, self.log_message, resumo, "SUCCESS" if falha_count == 0 else "WARNING")
                self.root.after(0, self._reset_progress)
                self.root.after(0, lambda: messagebox.showinfo("Lote Concluído", resumo))
                self.root.after(0, lote_window.destroy)

            threading.Thread(target=_run_batch, daemon=True).start()

        processar_btn = ttk.Button(
            btn_frame, text="▶  Processar Lote",
            command=processar_lote,
            bootstyle=SUCCESS, width=18,
        )
        processar_btn.pack(side=tk.RIGHT)
