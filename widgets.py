# -*- coding: utf-8 -*-
"""
    Widgets
    画面のパーツ
"""
from decimal import Decimal
from functools import partial
from tkinter import filedialog
import tkinter as tk
from typing import Optional
from pathlib import Path

from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

from controllers import AppController
from lib.models import MosaicFilter, StatusMessage
from lib.utils import round_up_decimal


class Tooltip:
    """
    ツールチップ
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.id = self.widget.after(500, self.show_tooltip)

    def leave(self, event=None):
        if hasattr(self, 'id'):
            self.widget.after_cancel(self.id)
            if self.tooltip:
                self.tooltip.destroy()
    
    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 32
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack(ipadx=1)


class PhotoImageButton(tk.Button):
    """
    イメージボタンクラス
    """
    def __init__(self, master=None, image_path: str = "", tooltip: Optional[Tooltip] = None, command=None, **kwargs):
        img = tk.PhotoImage(file=image_path)
        img = img.subsample(3, 3)
        if command is None:
            super().__init__(master, image=img, compound="top", **kwargs)
        else:
            super().__init__(master, image=img, compound="top", command=command, **kwargs)

        self.img = img  # Keep a reference to the image to prevent it from being garbage collected
        self.tooltip = tooltip


class HeaderFrame(tk.Frame):
    """
    画面のヘッダー部
    """
    def __init__(self, master, controller: AppController, bg: str, icons_path: Path):
        super().__init__(master, bg=bg)

        self.controller = controller
        self.btn_pick_images = PhotoImageButton(self,
                                                image_path=str(Path(icons_path, "file_open_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                                command=self.controller.handle_pick_images)
        self.btn_pick_images.tooltip = Tooltip(self.btn_pick_images, "Open")
        self.btn_pick_images.grid(row=0, column=0, padx=(0, 0))

        self.btn_back_file = PhotoImageButton(self,
                                              image_path=str(Path(icons_path, "arrow_back_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                              command=self.controller.handle_back_images)
        self.btn_back_file.tooltip = Tooltip(self.btn_back_file, "Back")
        self.btn_back_file.grid(row=0, column=1, padx=(4, 0))

        self.btn_forward_file = PhotoImageButton(self,
                                                 image_path=str(Path(icons_path, "arrow_forward_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                                 command=self.controller.handle_forward_images)
        self.btn_forward_file.tooltip = Tooltip(self.btn_forward_file, "Forward")
        self.btn_forward_file.grid(row=0, column=2, padx=(4, 0))

        self.widgetHeader = tk.Label(self, text="画面に画像ファイルをドラッグ＆ドロップしてください。", font=("", 10))
        self.widgetHeader.grid(row=0, column=3, padx=(4, 0))


class MainFrame(tk.Frame):
    """
    画面のメイン部
    """
    def __init__(self, master, controller: AppController, bg: str):
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

        # ドラッグ開始時のイベントをバインド
        self.canvas.bind("<Button-1>", self.start_drag)

        # ドラッグ中のイベントをバインド
        self.canvas.bind("<B1-Motion>", self.dragging)

        # ドラッグ終了時のイベントをバインド
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)
        self.photo = None

    def updateImage(self, filepath):
        if len(filepath) == 0:
            return
        #self.canvas.image = Image.open(filepath)
        #self.photo = ImageTk.PhotoImage(self.canvas.image)
        # 日本語ファイル名でエラーが発生するため。openを使用する。
        with open(filepath, "rb") as f:
            img = Image.open(f)
            self.original_image = img  # 元の画像を開く
            self.photo = ImageTk.PhotoImage(self.original_image)  # 元の画像のコピーをキャンバスに表示

        # 画像を更新
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        # キャンバスのスクロール領域を設定
        self.canvas.config(scrollregion=(0, 0, self.original_image.width, self.original_image.height))

    def start_drag(self, event):
        """
        ドラッグ開始
        """
        # ドラッグ開始位置を記録（キャンバス上の座標に変換）
        self.start_x = int(self.canvas.canvasx(event.x))
        self.start_y = int(self.canvas.canvasy(event.y))

    def dragging(self, event):
        """
        ドラッグ中
        """
        if self.photo is None:
            return
        # ドラッグ中は選択領域を表示
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        end_x = int(self.canvas.canvasx(event.x))
        end_y = int(self.canvas.canvasy(event.y))
        self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline='red', tags='dragging')

    def end_drag(self, event):
        """
        ドラッグ終了時
        """
        # ドラッグ終了位置を取得（キャンバス上の座標に変換）
        end_x = int(self.canvas.canvasx(event.x))
        end_y = int(self.canvas.canvasy(event.y))

        # 選択領域にモザイクをかける
        self.apply_mosaic(self.start_x, self.start_y, end_x, end_y)

        # ドラッグ中に表示した選択領域を削除
        self.canvas.delete('dragging')

    def apply_mosaic(self, start_x: int, start_y: int, end_x: int, end_y: int):
        """
        モザイクを適用します。
        """
        if self.photo is None:
            return

        # 座標を正しい順序に並べ替える
        left = min(start_x, end_x)
        right = max(start_x, end_x)
        top = min(start_y, end_y)
        bottom = max(start_y, end_y)

        mosaic = MosaicFilter(self.original_image)
        mosaic.apply(left, top, right, bottom)
        self.original_image = mosaic.Image

        self.photo = ImageTk.PhotoImage(self.original_image)  # 元の画像のコピーをキャンバスに表示
        # キャンバスの画像も更新
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        # キャンバスのスクロール領域を設定
        self.canvas.config(scrollregion=(0, 0, self.original_image.width, self.original_image.height))

        # モザイク適用後のファイルを保存します。
        mosaic.save(str(self.controller.get_new_file()))


class FooterFrame(tk.Frame):
    """
    画面のフッター部
    """
    def __init__(self, master, bg):
        super().__init__(master, bg=bg)

        self.imageSizeBar = tk.Label(self, text=" " * 40, bd=1, relief=tk.SUNKEN, anchor=tk.W)  # 画像サイズ表示用のラベルを追加
        self.imageSizeBar.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.count = tk.Label(self, text="  1 /  1 ", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.count.grid(row=0, column=1, sticky=tk.W + tk.E)
        self.fileSizeBar = tk.Label(self, text=" " * 20, bd=1, relief=tk.SUNKEN, anchor=tk.W)  # ファイルサイズ表示用のラベルを追加
        self.fileSizeBar.grid(row=0, column=2, sticky=tk.W + tk.E)
        self.modified = tk.Label(self, text=" " * 20, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.modified.grid(row=0, column=3, sticky=tk.W + tk.E)

        self.paddingLabel = tk.Label(self, text="フッターはここ")  # 余白調整用のラベルを追加
        self.paddingLabel.grid(row=0, column=4, sticky=tk.W + tk.E)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=1)  # 列2（余白調整用のラベル）にweightを設定

    def updateStatusBar(self, status: StatusMessage):
        """
        ステータスバーを更新します。
        """
        # 画像の幅と高さ
        self.imageSizeBar.config(text=f"Width: {status.width}px, Height: {status.height}px")
        # 件数
        self.count.config(text=f"{status.current} / {status.total}")
        # ファイルサイズ
        filesize_kb = Decimal(status.file_size) / Decimal(1024)
        self.fileSizeBar.config(text=str(round_up_decimal(Decimal(filesize_kb), 2)) + " KB")
        # 最終更新日時
        self.modified.config(text=status.mtime)

    def updateMessage(self, text: str):
        self.paddingLabel.config(text=text)


class MainPage(tk.Frame):
    """
    メインページ
    """
    def __init__(self, master: TkinterDnD.Tk, controller: AppController, icons_path: Path):
        super().__init__(master, bg="#00C8B4")
        self.controller = controller
        self.HeaderFrame = HeaderFrame(self, controller, "#44F7D3", icons_path)
        self.HeaderFrame.grid(column=0, row=0, sticky=(tk.E + tk.W + tk.S + tk.N))
        self.MainFrame = MainFrame(self, controller, bg="#88FFEB")
        self.MainFrame.grid(column=0, row=1, sticky=(tk.E + tk.W + tk.S + tk.N))
        self.FooterFrame = FooterFrame(self, bg="#FFBB9D")
        self.FooterFrame.grid(column=0, row=2, sticky=(tk.E + tk.W + tk.S + tk.N))

        # ヘッダーとフッターの行のweightを0に設定（固定領域）
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(2, weight=0)

        # メインフレームの行のweightを1に設定（残りのスペースをすべて取る）
        self.grid_rowconfigure(1, weight=1)

        self.columnconfigure(0, weight=1)  # ヘッダーをウィンドウ幅まで拡張する
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.controller.handle_drop)

    def display_image(self, path: Path):
        """
        画像ファイルを選択時
        """
        data = str(path)
        self.MainFrame.updateImage(data)
        self.controller.set_window_title(data)
        self.updateFileStatus()

    def on_select_files(self, event):
        """
        ファイル選択ボタン
        """
        # 画像形式
        ImageFormat = {
            'PNG': ('*.png', ),
            'JPEG': ('*.jpg', '*.jpeg', ),
            'WEBP': ('*.webp', ),
            'BMP': ('*.bmp', ),
            'PNM': ('*.pbm', '*.pgm', '*.ppm', )
        }
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

    def updateFileStatus(self):
        """
        フッターのステータスバーを更新
        """
        self.FooterFrame.updateStatusBar(self.controller.get_status())

    def status_message(self, text: str):
        self.FooterFrame.updateMessage(text)
