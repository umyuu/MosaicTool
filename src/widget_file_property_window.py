# -*- coding: utf-8 -*-
"""
    FilePropertyWindow
    ファイル情報の画面
"""
import tkinter as tk
from pathlib import Path

from . import PROGRAM_NAME
from . abstract_controllers import AbstractAppController
from . app_config import FontSize, ThemeColors
from . models import StatusBarInfo
from . widgets_core import LabelTextEntry, RightClickMenu


class FilePropertyWindow:
    """
    ファイルプロパティウィンドウ
    """
    def __init__(self, master, controller: AbstractAppController):
        """
        コンストラクタ
        :param master: 親Widget
        :param controller: コントローラー
        """
        self.controller = controller

        config = self.controller.get_config()
        font_sizes = config.font_sizes
        theme_colors = config.theme_colors

        width, height = config.get("window_sizes").get("file_property")
        self.win = tk.Toplevel(master, bg=theme_colors.bg_neutral)
        self.win.title(f"{PROGRAM_NAME} - File Property")
        self.win.geometry(f"{width}x{height}")
        self.win.protocol('WM_DELETE_WINDOW', self.on_window_close)

        self.main_frame = tk.Frame(self.win, bg=theme_colors.bg_neutral, width=width)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.right_click_menu = RightClickMenu(self.win)

        self.setup_file_info(font_sizes, theme_colors)
        self.setup_footer(font_sizes, theme_colors)
        self.setup_right_click_menu_bind()

        # Widgetの配置
        self.setup_grid()

    def setup_file_info(self, font_sizes: FontSize, theme_colors: ThemeColors):
        """ファイル情報の設定を行います。

        :param font_sizes: フォントサイズ情報
        :param theme_colors: テーマ色
        """
        self.info_frame = tk.LabelFrame(self.main_frame,
                                        bg=theme_colors.bg_neutral, text="File Property", font=("", font_sizes.h5))

        self.file_name_var = tk.StringVar()
        self.file_name_var.set("")
        self.file_name = tk.Entry(self.info_frame,
                                  font=("", font_sizes.body),
                                  bg=theme_colors.bg_white,
                                  textvariable=self.file_name_var)

        self.folder = LabelTextEntry(self.info_frame, text="Folder:", font=("", font_sizes.body), textvariable=None)
        self.folder.set_label_background_color(theme_colors.bg_neutral)
        self.folder.set_text_background_color(theme_colors.bg_white)

        self.full_path = LabelTextEntry(self.info_frame, text="Full Path:", font=("", font_sizes.body), textvariable=None)
        self.full_path.set_label_background_color(theme_colors.bg_neutral)
        self.full_path.set_text_background_color(theme_colors.bg_white)

        self.mosaic_file_name = LabelTextEntry(self.info_frame,
                                               text="Mosaic File:", font=("", font_sizes.body), textvariable=None)
        self.mosaic_file_name.set_label_background_color(theme_colors.bg_neutral)
        self.mosaic_file_name.set_text_background_color(theme_colors.bg_white)

        self.action_folder_mask = tk.Button(self.info_frame,
                                            text="Folder Mask", bd=1, bg=theme_colors.bg_secondary,
                                            relief=tk.RAISED, anchor=tk.W,
                                            command=self.handle_folder_mask, font=("", font_sizes.body), pady=4)

        self.action_copy = tk.Button(self.info_frame, text="Copy Extra Text", bd=1, bg=theme_colors.bg_secondary,
                                     relief=tk.RAISED, anchor=tk.W, 
                                     command=self.handle_copy_text, font=("", font_sizes.body), pady=4)

        self.setup_extra(font_sizes, theme_colors)

    def setup_extra(self, font_sizes: FontSize, theme_colors: ThemeColors):
        """
        EXIFとPNGInfo表示領域の設定を行います。

        :param font_sizes: フォントサイズ情報
        :param theme_colors: テーマ色
        """
        self.extra_frame = tk.LabelFrame(self.info_frame, bg=theme_colors.bg_neutral, text="Extra", font=("", font_sizes.h5))
        self.extra_text = tk.Text(self.extra_frame, bd=1, relief=tk.SUNKEN)
        # スクロールバーの作成
        self.extra_text_scrollbar = tk.Scrollbar(self.extra_text, command=self.extra_text.yview)
        # Textウィジェットとスクロールバーを連動させる
        self.extra_text.config(yscrollcommand=self.extra_text_scrollbar.set)

        self.extra_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0), pady=4)
        self.extra_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_footer(self, font_sizes: FontSize, theme_colors: ThemeColors):
        """
        フッターの設定を行います。

        :param font_sizes: フォントサイズ情報
        :param theme_colors: テーマ色
        """
        self.footer_frame = tk.Frame(self.main_frame, bg=theme_colors.bg_neutral)
        self.action_ok = tk.Button(self.footer_frame, text="OK", relief=tk.RAISED, bg=theme_colors.bg_primary,
                                   command=self.on_window_close, font=("", font_sizes.h3))
        self.action_ok.pack(fill=tk.X)

    def setup_grid(self):
        """Widgetを配置します。"""
        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(0, weight=1)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid(row=0, column=0, padx=8, sticky="nsew")
        self.footer_frame.grid(row=1, column=0, padx=8, pady=8, sticky="ew")

        self.info_frame.rowconfigure(5, weight=1)
        self.info_frame.columnconfigure(0, weight=1)
        self.info_frame.columnconfigure(1, weight=1)

        self.file_name.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(4, 0))
        self.folder.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=(4, 0))
        self.full_path.grid(row=2, column=0, columnspan=2, sticky="ew", padx=4, pady=(4, 0))
        self.mosaic_file_name.grid(row=3, column=0, columnspan=2, sticky="ew", padx=4, pady=(4, 0))
        self.action_folder_mask.grid(row=4, column=0, sticky="ew", padx=4, pady=(4, 0))
        self.action_copy.grid(row=4, column=1, sticky="ew", padx=4, pady=(4, 0))
        self.extra_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=4, pady=(4, 0))

    def setup_right_click_menu_bind(self):
        """
        右クリックメニューにテキスト項目をbindします。
        """
        for entry in (self.file_name,
                      self.folder.text_entry,
                      self.full_path.text_entry,
                      self.mosaic_file_name.text_entry,
                      self.extra_text):
            entry.bind("<Button-3>", self.right_click_menu.on_show_menu)

    def handle_folder_mask(self):
        """
        フォルダーマスクボタン
        """
        self.folder.set_text("")
        self.full_path.set_text("")
        self.mosaic_file_name.set_text("")

    def handle_copy_text(self):
        """
        コピーボタン
        クリップボードにコピーします。
        """
        text = self.extra_text.get("1.0", "end-1c")  # 1行目から最後の文字を取得
        self.win.clipboard_clear()  # クリップボードをクリア
        self.win.clipboard_append(text)  # テキストをクリップボードに追加

    def on_window_open(self):
        """
        ファイル情報を開く
        """
        self.win.deiconify()
        self.controller.set_file_property_visible(True)

    def on_window_close(self):
        """
        ファイル情報ウィンドウを閉じる
        """
        self.win.withdraw()
        self.controller.set_file_property_visible(False)

    def set_file_status(self, status: StatusBarInfo):
        """
        ファイル情報を表示します。
        :param status: ファイル情報
        """
        file_path: Path = status.file_path

        self.file_name_var.set(file_path.name)
        self.folder.set_text(str(file_path.parent))
        self.full_path.set_text(str(file_path))
        self.mosaic_file_name.set_text(str(self.controller.get_mosaic_filename().name))

    def set_extra_text(self, text: str):
        """
        拡張情報を設定します。
        :param text: 設定するテキスト
        """
        self.extra_text.delete("1.0", "end")  # テキスト全体を削除
        self.extra_text.insert("1.0", text)  # 新しいテキストを挿入
