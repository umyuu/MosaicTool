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

from PIL import ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

from . app_config import FontSize, ThemeColors
from . abstract_controllers import AbstractAppController
from . models import MosaicFilter, StatusBarInfo, ImageFormat
from . utils import round_up_decimal, Stopwatch
from . widgets_core import WidgetUtils, PhotoImageButton, Tooltip, LabelTextEntry, RightClickMenu
from . image_file_service import ImageFileService

PROGRAM_NAME = 'MosaicTool'


class HeaderFrame(tk.Frame):
    """
    画面のヘッダー部
    """
    def __init__(self, master, controller: AbstractAppController, bg: str, icons_path: Path):
        super().__init__(master, bg=bg)
        self.controller = controller

        theme_colors = self.controller.theme_colors
        # Widgetを生成します。
        self.action_file_open = PhotoImageButton(self,
                                                 image_path=str((icons_path / "file_open_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                                 tooltip_text="Open (Ctrl+O)",
                                                 bg=theme_colors.bg_secondary,
                                                 command=self.controller.handle_file_open)
        self.action_save_as = PhotoImageButton(self,
                                               image_path=str((icons_path / "save_as_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                               tooltip_text="SaveAs (Ctrl+Shift+S)",
                                               bg=theme_colors.bg_secondary,
                                               command=self.controller.handle_save_as)
        self.action_back = PhotoImageButton(self,
                                            image_path=str((icons_path / "arrow_back_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                            tooltip_text="Previous file (<-)",
                                            bg=theme_colors.bg_secondary,
                                            command=self.controller.handle_back_image)
        self.action_forward = PhotoImageButton(self,
                                               image_path=str((icons_path / "arrow_forward_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                               tooltip_text="Next file (->)",
                                               bg=theme_colors.bg_secondary,
                                               command=self.controller.handle_forward_image)
        self.action_file_info = PhotoImageButton(self,
                                                 image_path=str((icons_path / "info_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                                 tooltip_text="Image Information (I)",
                                                 bg=theme_colors.bg_secondary,
                                                 command=self.controller.on_show_file_property)

        font_size_h4: int = self.controller.font_sizes.h4
        self.widgetHeader = tk.Label(self, bg=theme_colors.bg_primary,
                                     text="画面にフォルダまたはファイルをドラッグ＆ドロップしてください。",
                                     font=("", font_size_h4))

        # Widgetを配置します。
        self.action_file_open.grid(row=0, column=0, padx=(0, 0))
        self.action_save_as.grid(row=0, column=1, padx=(4, 0))
        self.action_back.grid(row=0, column=2, padx=(4, 0))
        self.action_forward.grid(row=0, column=3, padx=(4, 0))
        self.action_file_info.grid(row=0, column=4, padx=(4, 0))
        self.widgetHeader.grid(row=0, column=5, padx=(4, 0))

        # キーバインドの設定をします。
        WidgetUtils.bind_all(self, "Control", "O", partial(self.controller.handle_file_open))
        WidgetUtils.bind_all(self, "Control-Shift", "S", partial(self.controller.handle_save_as))
        WidgetUtils.bind_all(self, "", "Left", partial(self.controller.handle_back_image))
        WidgetUtils.bind_all(self, "Shift", "Left", partial(self.controller.handle_back_image))
        WidgetUtils.bind_all(self, "", "Right", partial(self.controller.handle_forward_image))
        WidgetUtils.bind_all(self, "Shift", "Right", partial(self.controller.handle_forward_image))
        WidgetUtils.bind_all(self, "", "I", partial(self.controller.on_show_file_property))


class MainFrame(tk.Frame):
    """
    画面のメイン部
    ToDo:ImageEditorクラスを新設する予定です。
    """
    def __init__(self, master, controller: AbstractAppController, bg: str):
        super().__init__(master, bg=bg)

        self.controller = controller
        # 水平スクロールバーを追加
        self.hscrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 垂直スクロールバーを追加
        self.vscrollbar = tk.Scrollbar(self)
        self.vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # キャンバスを作成し、スクロールバーを設定
        self.canvas = tk.Canvas(self, yscrollcommand=self.vscrollbar.set, xscrollcommand=self.hscrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # スクロールバーのコマンドを設定
        self.vscrollbar.config(command=self.canvas.yview)
        self.hscrollbar.config(command=self.canvas.xview)

        self.photo = None
        # モザイク領域の選択開始位置
        self.start_x = 0
        self.start_y = 0
        self.rect_tag = None  # 矩形のタグ
        self.size_label = None  # サイズ表示用ラベル
        # ドラッグ開始時のイベントをバインド
        self.canvas.bind("<Button-1>", self.handle_start_drag)

        # ドラッグ中のイベントをバインド
        self.canvas.bind("<B1-Motion>", self.handle_dragging)

        # ドラッグ終了時のイベントをバインド
        self.canvas.bind("<ButtonRelease-1>", self.handle_end_drag)

    def updateImage(self, filepath: Path):
        """
        表示画像を更新します。
        :param filepath: 画像ファイルパス
        """
        if not filepath.exists():
            return
        self.original_image = ImageFileService.load(filepath)  # 元の画像を開く
        self.photo = ImageTk.PhotoImage(self.original_image)  # 元の画像のコピーをキャンバスに表示
        # 画像を更新
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        # キャンバスのスクロール領域を設定
        self.canvas.config(scrollregion=(0, 0, self.original_image.width, self.original_image.height))

    def handle_start_drag(self, event):
        """
        ドラッグ開始
        """
        # ドラッグ開始位置を記録（キャンバス上の座標に変換）
        self.start_x = int(self.canvas.canvasx(event.x))
        self.start_y = int(self.canvas.canvasy(event.y))

    def handle_dragging(self, event):
        """
        ドラッグ中
        """
        end_x = int(self.canvas.canvasx(event.x))
        end_y = int(self.canvas.canvasy(event.y))

        # 矩形が既に存在する場合は削除します。
        if self.rect_tag:
            self.canvas.delete(self.rect_tag)
        if self.size_label:
            self.canvas.delete(self.size_label)

        # 矩形を描画し、タグを付けます。
        self.rect_tag = self.canvas.create_rectangle(
            self.start_x, self.start_y, end_x, end_y,
            outline=self.controller.get_config().theme_colors.bg_danger)

        # サイズを計算して表示します。
        width = abs(end_x - self.start_x)
        height = abs(end_y - self.start_y)

        # サイズラベルの位置をマウスカーソルの近くに設定します。
        label_x = end_x + 10
        label_y = end_y + 10
        # font sizeを固定から修正します。
        self.size_label = self.canvas.create_text(
            (label_x, label_y),
            font=("", self.controller.get_config().font_sizes.h5), text=f"{width} x {height}",
            anchor="nw")

    def handle_end_drag(self, event):
        """
        ドラッグ終了時
        """
        try:
            sw = Stopwatch.start_new()
            # ドラッグ終了位置を取得します。（キャンバス上の座標に変換）
            end_x = int(self.canvas.canvasx(event.x))
            end_y = int(self.canvas.canvasy(event.y))

            # 選択領域にモザイクをかけます。
            is_apply = self.apply_mosaic(self.start_x, self.start_y, end_x, end_y)
            if is_apply:
                self.controller.display_process_time(f"{sw.elapsed:.3f}s")
        except Exception as e:
            print(f"Error applying mosaic: {e}")
            raise e
        finally:
            # 矩形とサイズ表示用ラベルを削除
            if self.rect_tag:
                self.canvas.delete(self.rect_tag)
            if self.size_label:
                self.canvas.delete(self.size_label)

    def apply_mosaic(self, start_x: int, start_y: int, end_x: int, end_y: int) -> bool:
        """
        モザイクを適用します。
        :return: モザイクを掛けてたかどうか
        """
        if self.photo is None:
            return False

        # 座標を正しい順序に並べ替える
        left = min(start_x, end_x)
        right = max(start_x, end_x)
        top = min(start_y, end_y)
        bottom = max(start_y, end_y)

        mosaic = MosaicFilter(self.original_image)
        is_apply = mosaic.apply(left, top, right, bottom)
        if not is_apply:
            return False

        self.original_image = mosaic.Image
        self.photo = ImageTk.PhotoImage(self.original_image)  # 元の画像のコピーをキャンバスに表示
        # キャンバスの画像も更新
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        # キャンバスのスクロール領域を設定
        #self.canvas.config(scrollregion=(0, 0, self.original_image.width, self.original_image.height))

        # モザイク適用後のファイルを自動保存します。
        self.save(self.controller.get_mosaic_filename())
        return True

    def save(self, output_path: Path, override: bool = False):
        """
        モザイク画像を保存します。
        :param output_path: 保存するファイルの名前
        :param override: 自動保存時に上書きするかの確認
        """
        current_file = self.controller.get_current_image()

        # 自動保存時に同一ファイル名の場合は、念のため確認メッセージを表示します。
        if not override:
            if current_file == output_path:
                retval = messagebox.askokcancel(
                    PROGRAM_NAME,
                    f"{output_path}は既に存在します。\n上書きしますか？")
                if not retval:
                    return

        ImageFileService.save(self.original_image, output_path, current_file)


class FooterFrame(tk.Frame):
    """
    画面のフッター部
    """
    def __init__(self, master, bg: str):
        super().__init__(master, bg=bg)

        # Widgetの生成
        self.image_size = tk.Label(self, text=" ", bd=1, relief=tk.SUNKEN, anchor=tk.W)  # 画像サイズ表示用のラベルを追加
        self.image_size.tooltip = Tooltip(self.image_size, "Width x Height")

        self.count = tk.Label(self, text="  1 /  1 ", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.count.tooltip = Tooltip(self.count, "Current / Total")

        self.fileSizeBar = tk.Label(self, text=" ", bd=1, relief=tk.SUNKEN, anchor=tk.W)  # ファイルサイズ表示用のラベルを追加
        self.fileSizeBar.tooltip = Tooltip(self.fileSizeBar, "File Size")

        self.modified = tk.Label(self, text=" ", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.modified.tooltip = Tooltip(self.modified, "モザイク加工対象ファイルの最終更新日時")

        self.paddingLabel = tk.Label(self, text="フッターはここ", anchor=tk.E)  # 余白調整用のラベルを追加
        self.process_time = tk.Label(self, text=" ", anchor=tk.E)
        self.process_time.tooltip = Tooltip(self.process_time, "処理時間(sec)")

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


class FilePropertyWindow:
    """
    ファイルプロパティウィンドウ
    """
    def __init__(self, master, controller: AbstractAppController):
        self.controller = controller

        config = self.controller.get_config()
        font_sizes = config.font_sizes
        theme_colors = config.theme_colors

        window_size = config.get("filePropertyWindowSize", {"width": 500, "height": 500})
        width = window_size.get("width")
        height = window_size.get("height")
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
        """ファイル情報の設定を行います。"""
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
        """EXIFとPNGInfo表示領域の設定を行います。"""
        self.extra_frame = tk.LabelFrame(self.info_frame, bg=theme_colors.bg_neutral, text="Extra", font=("", font_sizes.h5))
        self.extra_text = tk.Text(self.extra_frame, bd=1, relief=tk.SUNKEN)
        # スクロールバーの作成
        self.extra_text_scrollbar = tk.Scrollbar(self.extra_text, command=self.extra_text.yview)
        # Textウィジェットとスクロールバーを連動させる
        self.extra_text.config(yscrollcommand=self.extra_text_scrollbar.set)

        self.extra_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0), pady=4)
        self.extra_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_footer(self, font_sizes: FontSize, theme_colors: ThemeColors):
        """フッターの設定を行います。"""
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
        :param text: 表示するテキスト
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


class MainPage(tk.Frame):
    """
    メインページ
    """
    def __init__(self, master: TkinterDnD.Tk, controller: AbstractAppController, icons_path: Path):
        super().__init__(master, bg=controller.get_config().theme_colors.bg_neutral)
        self.controller = controller

        config = self.controller.get_config()
        self.file_property_window: Optional[FilePropertyWindow] = None
        # Widgetの生成
        self.HeaderFrame = HeaderFrame(self, controller, config.theme_colors.bg_primary, icons_path)
        self.MainFrame = MainFrame(self, controller, bg=config.theme_colors.bg_neutral)
        self.FooterFrame = FooterFrame(self, bg=config.theme_colors.text_info)

        self.setup_bindings()

        # イベントを登録します。
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.controller.handle_drop)
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
        画像ファイルを選択時
        :param event: 画像ファイルのパス
        """
        self.MainFrame.updateImage(file_path)
        self.controller.set_window_title(file_path)
        self.controller.update_status_bar_file_info()

    def handle_file_open(self, event):
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
            ('*', '*.*')
        ]

        files = filedialog.askopenfilenames(parent=self, filetypes=IMAGE_FILE_TYPES)
        if len(files) == 0:
            return
        self.controller.handle_select_files_complete(files)

    def handle_save_as(self, event):
        """
        ファイルを選択して保存ボタン
        :param event: イベント
        """
        if not hasattr(self.MainFrame, "original_image"):
            return

        IMAGE_FILE_TYPES = [
            ('Image Files', ImageFormat['PNG'] + ImageFormat['JPEG'] + ImageFormat['WEBP'] + ImageFormat['BMP']),
            ('png (*.png)', ImageFormat['PNG']),
            ('jpg (*.jpg, *.jpeg)', ImageFormat['JPEG']),
            ('webp (*.webp)', ImageFormat['WEBP']),
            ('bmp (*.bmp)', ImageFormat['BMP']),
            ('*', '*.*')
        ]

        files = filedialog.asksaveasfilename(parent=self, confirmoverwrite=True, filetypes=IMAGE_FILE_TYPES)
        if len(files) == 0:
            return

        save_file = Path(files)
        if len(save_file.suffix) == 0:
            retval = messagebox.askokcancel(PROGRAM_NAME,
                                            f"ファイル名に拡張子が付与されていません\n{save_file}\n\nOK:ファイル名の選択に戻る\nCancel:名前を付けて保存の処理を中断する。")
            if not retval:
                print(f"名前を付けて保存の処理を中断。:{save_file}")
                return
            self.handle_save_as(event)
            return
        sw = Stopwatch.start_new()
        self.MainFrame.save(save_file, True)

        self.set_status_message(f"Save。{save_file.name}", f"{sw.elapsed:.3f}")
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
