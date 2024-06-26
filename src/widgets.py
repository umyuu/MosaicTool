# -*- coding: utf-8 -*-
"""
    Widgets
    画面パーツ
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from functools import partial
from decimal import Decimal
from pathlib import Path
from typing import Optional

from tkinterdnd2 import DND_FILES, TkinterDnD

from . import PROGRAM_NAME
from . abstract_controllers import AbstractAppController
from . models import StatusBarInfo, ImageFormat
from . utils import round_up_decimal, Stopwatch
from . widgets_core import WidgetUtils, PhotoImageButton, Tooltip
from . widget_file_property_window import FilePropertyWindow
from . widget_image_canvas import ImageCanvas
from . effects.image_effects import MosaicEffect


class HeaderFrame(tk.Frame):
    """
    画面のヘッダー部
    """
    def __init__(self, master, controller: AbstractAppController):
        """
        コンストラクタ
        :param master: 親Widget
        :param controller: コントローラー
        """
        super().__init__(master, bg=controller.theme_colors.bg_primary)
        self.controller = controller

        theme_colors = controller.theme_colors
        font_sizes = controller.font_sizes
        icons_path = controller.icons_path
        # Widgetを生成します。
        self.action_file_open = PhotoImageButton(
            self,
            image_path=str((icons_path / "file_open_24dp_FILL0_wght400_GRAD0_opsz24.png")),
            tooltip_text="Open (Ctrl+O)",
            bg=theme_colors.bg_secondary,
            command=self.controller.on_file_open)
        self.action_save_as = PhotoImageButton(
            self,
            image_path=str((icons_path / "save_as_24dp_FILL0_wght400_GRAD0_opsz24.png")),
            tooltip_text="SaveAs (Ctrl+Shift+S)",
            bg=theme_colors.bg_secondary,
            command=self.controller.on_save_as)
        self.action_back = PhotoImageButton(
            self,
            image_path=str((icons_path / "arrow_back_24dp_FILL0_wght400_GRAD0_opsz24.png")),
            tooltip_text="Previous file (<-)",
            bg=theme_colors.bg_secondary,
            command=self.controller.handle_back_image)
        self.action_forward = PhotoImageButton(
            self,
            image_path=str((icons_path / "arrow_forward_24dp_FILL0_wght400_GRAD0_opsz24.png")),
            tooltip_text="Next file (->)",
            bg=theme_colors.bg_secondary,
            command=self.controller.handle_next_image)
        self.action_file_info = PhotoImageButton(
            self,
            image_path=str((icons_path / "info_24dp_FILL0_wght400_GRAD0_opsz24.png")),
            tooltip_text="Image Information (I)",
            bg=theme_colors.bg_secondary,
            command=self.controller.on_show_file_property)

        self.mosaic_size = tk.Label(self, bg=theme_colors.bg_primary,
                                    text="モザイクサイズ：",
                                    font=("", font_sizes.h5))

        self.action_mosaic_size_change = tk.Button(
            self,
            bg=theme_colors.bg_secondary,
            font=("", font_sizes.h4),
            width=6,
            command=self.controller.handle_next_effect)
        self.action_mosaic_size_change_tooltip = Tooltip(self.action_mosaic_size_change,
                                                         "次のセルサイズに変更(Right Click)。 前のセルサイズに変更(Shift+Right Click)")
        self.update_view(None)

        self.widgetHeader = tk.Label(self, bg=theme_colors.bg_primary)

        # Widgetを配置します。
        self.action_file_open.grid(row=0, column=0, padx=(0, 0))
        self.action_save_as.grid(row=0, column=1, padx=(4, 0))
        self.action_back.grid(row=0, column=2, padx=(4, 0))
        self.action_forward.grid(row=0, column=3, padx=(4, 0))
        self.action_file_info.grid(row=0, column=4, padx=(4, 0))
        self.mosaic_size.grid(row=0, column=5, padx=(8, 0))
        self.action_mosaic_size_change.grid(row=0, column=6, padx=(4, 4))
        self.widgetHeader.grid(row=0, column=7, padx=(4, 0))

        # キーバインドの設定をします。
        WidgetUtils.bind_all(self, "Control", "O", partial(self.controller.on_file_open))
        WidgetUtils.bind_all(self, "Control-Shift", "S", partial(self.controller.on_save_as))
        WidgetUtils.bind_all(self, "", "Left", partial(self.controller.handle_back_image))
        WidgetUtils.bind_all(self, "Shift", "Left", partial(self.controller.handle_back_image))
        WidgetUtils.bind_all(self, "", "Right", partial(self.controller.handle_next_image))
        WidgetUtils.bind_all(self, "Shift", "Right", partial(self.controller.handle_next_image))
        WidgetUtils.bind_all(self, "", "I", partial(self.controller.on_show_file_property))

    def update_view(self, event):
        """
        Viewを更新します。
        :param event: イベント
        """
        current_effect = self.controller.current_effect
        if current_effect.cell_size == MosaicEffect.AUTO:
            self.action_mosaic_size_change.configure(text="AUTO")
        else:
            self.action_mosaic_size_change.configure(text=f"{current_effect.cell_size}")


class MainFrame(tk.Frame):
    """
    画面のメイン部
    """
    def __init__(self, master, controller: AbstractAppController):
        """
        コンストラクタ
        :param master: 親Widget
        :param controller: コントローラー
        """
        super().__init__(master, bg=controller.theme_colors.bg_neutral)

        self.controller = controller

        # 画面のキャンバス部分
        self.image_canvas = ImageCanvas(self, controller)
        self.image_canvas.pack(fill=tk.BOTH, expand=True)

        # イベントを登録します。
        self.update_view = self.image_canvas.update_view
        self.save = self.image_canvas.save


class FooterFrame(tk.Frame):
    """
    画面のフッター部
    """
    def __init__(self, master, controller: AbstractAppController):
        """
        コンストラクタ
        :param master: 親Widget
        :param controller: コントローラー
        """
        super().__init__(master, bg=controller.theme_colors.text_info)

        # Widgetの生成
        self.image_size = tk.Label(self, text=" ", bd=1, relief=tk.SUNKEN, anchor=tk.W)  # 画像サイズ表示用のラベルを追加
        self.image_size_tooltip = Tooltip(self.image_size, "Width x Height")

        self.count = tk.Label(self, text="  1 /  1 ", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.count_tooltip = Tooltip(self.count, "Current / Total")

        self.fileSizeBar = tk.Label(self, text=" ", bd=1, relief=tk.SUNKEN, anchor=tk.W)  # ファイルサイズ表示用のラベルを追加
        self.fileSizeBar_tooltip = Tooltip(self.fileSizeBar, "File Size")

        self.modified = tk.Label(self, text=" ", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.modified_tooltip = Tooltip(self.modified, "モザイク加工対象ファイルの最終更新日時")

        self.paddingLabel = tk.Label(self, text="フッターはここ", anchor=tk.E)  # 余白調整用のラベルを追加
        self.process_time = tk.Label(self, text=" ", anchor=tk.E)
        self.process_time_tooltip = Tooltip(self.process_time, "処理時間(sec)")

        # Widgetの配置
        self.image_size.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.count.grid(row=0, column=1, sticky=tk.W + tk.E)
        self.fileSizeBar.grid(row=0, column=2, sticky=tk.W + tk.E)
        self.modified.grid(row=0, column=3, sticky=tk.W + tk.E)
        self.paddingLabel.grid(row=0, column=4, sticky=tk.W + tk.E)
        self.process_time.grid(row=0, column=5, sticky=tk.W + tk.E)

        self.columnconfigure(0, weight=1, minsize=56)
        self.columnconfigure(1, weight=1, minsize=40)
        self.columnconfigure(2, weight=1, minsize=48)
        self.columnconfigure(3, weight=1, minsize=64)
        self.columnconfigure(4, weight=1, minsize=400)  # 余白調整用のラベル）にweightを設定
        self.columnconfigure(5, weight=1, minsize=24)

    def update_status_bar(self, info: StatusBarInfo):
        """
        ステータスバーを更新します。
        :param info: ステータスバーの情報
        """
        # 画像の幅と高さ
        self.image_size.config(text=f"{info.width} x {info.height}")
        # 件数
        self.count.config(text=f"{info.current} / {info.total}")
        # ファイルサイズ
        filesize_kb = Decimal(info.file_size) / Decimal(1024)
        self.fileSizeBar.config(text=str(round_up_decimal(Decimal(filesize_kb), 2)) + " KB")
        # 最終更新日時
        self.modified.config(text=info.mtime)

    def updateMessage(self, text: str):
        """
        ステータスバーのメッセージ欄欄
        :param text: 表示するテキスト
        """
        self.paddingLabel.config(text=text)

    def update_process_time(self, text: str):
        """
        ステータスバーの処理時間欄
        :param text: 表示するテキスト
        """
        self.process_time.config(text=text)


class MainPage(tk.Frame):
    """
    メインページ
    """
    def __init__(self, master: TkinterDnD.Tk, controller: AbstractAppController):
        """
        コンストラクタ
        :param master: 親Widget
        :param controller: コントローラー
        """
        super().__init__(master, bg=controller.theme_colors.bg_neutral)
        self.controller = controller

        self.file_property_window: Optional[FilePropertyWindow] = None
        # Widgetの生成
        self.HeaderFrame = HeaderFrame(self, controller)
        self.MainFrame = MainFrame(self, controller)
        self.FooterFrame = FooterFrame(self, controller)

        self.setup_bindings()

        # イベントを登録します。
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.controller.handle_drop)
        self.update_header_view = self.HeaderFrame.update_view
        self.on_save = self.MainFrame.save
        self.on_update_status_bar = self.FooterFrame.update_status_bar
        self.on_update_process_time = self.FooterFrame.update_process_time

    def setup_bindings(self):
        """
        Widgetの配置
        """
        self.HeaderFrame.grid(column=0, row=0, sticky=(tk.E + tk.W + tk.S + tk.N))
        self.MainFrame.grid(column=0, row=1, sticky=(tk.E + tk.W + tk.S + tk.N))
        self.FooterFrame.grid(column=0, row=2, sticky=(tk.E + tk.W + tk.S + tk.N))
        # ヘッダーとフッターの行のweightを0に設定（固定領域）
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(2, weight=0)
        # メインフレームの行のweightを1に設定（残りのスペースをすべて取る）
        self.grid_rowconfigure(1, weight=1)
        # ヘッダーをウィンドウ幅まで拡張する
        self.columnconfigure(0, weight=1)  

    #def apply_theme(self, config: AppConfig):
    #    from tkinter import ttk
    #    self.configure(bg=config.neutral_hue)
    #    style = ttk.Style()
    #    style.theme_use('classic')
    #    style.configure('TLabel', background=config.neutral_hue, font=("", config.font_sizes.h1))
    #    style.configure('TButton', background=config.primary_hue, font=("", config.font_sizes.body))
    #    style.configure('TFrame', background=config.neutral_hue)
    #    style.configure('TLabelframe', background=config.neutral_hue)
    #    style.configure('TLabelframe.Label', background=config.neutral_hue, font=("", config.font_sizes.body))
    #    style.configure('TButton', foreground='blue')
    #    self.style = style

    def display_image(self, file_path: Path):
        """
        画面に画像イメージを表示します。
        :param event: 画像ファイルのパス
        """
        self.HeaderFrame.update_view(None)
        self.MainFrame.update_view(file_path)
        self.controller.set_window_title(file_path)
        self.controller.update_status_bar_file_info()

    def on_file_open(self, event):
        """
        ファイル選択ボタン
        :param event: イベント
        """
        IMAGE_FILE_TYPES = [
            ('Image Files', ImageFormat['PNG'] + ImageFormat['JPEG'] + ImageFormat['WEBP'] + ImageFormat['BMP']),
            ('png (*.png)', ImageFormat['PNG']),
            ('jpg (*.jpg, *.jpeg)', ImageFormat['JPEG']),
            ('webp (*.webp)', ImageFormat['WEBP']),
            ('bmp (*.bmp)', ImageFormat['BMP']),
            ('All Files', '*.*')
        ]

        current = self.controller.get_current_image()
        initialdir = None
        if current is not None:
            initialdir = current.parent

        files = filedialog.askopenfilenames(parent=self, initialdir=initialdir, filetypes=IMAGE_FILE_TYPES)
        if len(files) == 0:
            return
        self.controller.handle_select_files_complete(files)

    def on_save_as(self, event, initial_file: Path):
        """
        ファイルを選択して保存ボタン
        :param event: イベント
        :param initial_file: ダイアログのファイル名(初期値)
        """
        IMAGE_FILE_TYPES = [
            ('Image Files', ImageFormat['PNG'] + ImageFormat['JPEG'] + ImageFormat['WEBP'] + ImageFormat['BMP']),
            ('png (*.png)', ImageFormat['PNG']),
            ('jpg (*.jpg, *.jpeg)', ImageFormat['JPEG']),
            ('webp (*.webp)', ImageFormat['WEBP']),
            ('bmp (*.bmp)', ImageFormat['BMP']),
            ('All Files', '*.*')
        ]

        # フォルダをドロップ時は、モザイクフォルダが存在しません。
        # フォルダを開く前にモザイクフォルダを作成します。
        parent_dir = initial_file.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True)

        files = filedialog.asksaveasfilename(parent=self,
                                             initialdir=parent_dir,
                                             initialfile=initial_file.name,
                                             confirmoverwrite=True,
                                             filetypes=IMAGE_FILE_TYPES)
        if len(files) == 0:
            return

        save_file = Path(files)
        if len(save_file.suffix) == 0:
            retval = messagebox.askokcancel(PROGRAM_NAME,
                                            f"ファイル名に拡張子が付与されていません\n{save_file}\n\nOK:ファイル名の選択に戻る\nCancel:名前を付けて保存の処理を中断する。")
            if not retval:
                print(f"名前を付けて保存の処理を中断。:{save_file}")
                return
            self.on_save_as(event, initial_file)
            return
        sw = Stopwatch.start_new()
        self.on_save(save_file, True)

        self.set_status_message(f"Save. {save_file.name}", f"{sw.elapsed:.3f}")
        messagebox.showinfo(PROGRAM_NAME, f"ファイルを保存しました。\n\n{save_file}")

    def set_status_message(self, text: str, time: str = ""):
        """
        フッターのステータスバーのメッセージ欄
        :param text: メッセージ欄に表示するテキスト
        :param time: 処理時間欄に表示するテキスト
        """
        self.FooterFrame.updateMessage(text)
        if time:
            self.on_update_process_time(time)

    def on_show_file_property(self, status: StatusBarInfo, image_info):
        """
        ファイルのプロパティ画面を表示します。
        :param status: ステータスバーの情報
        :param image_info: Exif/PNGinfoの情報
        """
        if self.file_property_window is None:
            self.file_property_window = FilePropertyWindow(self, self.controller)

        self.file_property_window.set_file_status(status)
        if image_info:
            self.file_property_window.set_extra_text(image_info)
        else:
            self.file_property_window.set_extra_text("")

        self.after(1, self.file_property_window.on_window_open)    
