# -*- coding: utf-8 -*-
"""
    PhotoImageButton
"""
from decimal import Decimal
from functools import partial
import tkinter as tk

from pathlib import Path

from PIL import Image, ImageTk

from controllers import AppController
from lib.models import MosaicImageFile, MosaicImage
from lib.utils import round_up_decimal


class PhotoImageButton(tk.Button):
    """
    イメージボタンクラス
    """
    def __init__(self, master=None, image_path="", command=None, **kwargs):
        img = tk.PhotoImage(file=image_path)
        img = img.subsample(3, 3)
        if command is None:
            super().__init__(master, image=img, compound="top", **kwargs)
        else:
            super().__init__(master, image=img, compound="top", command=command, **kwargs)

        self.img = img  # Keep a reference to the image to prevent it from being garbage collected


class HeaderFrame(tk.Frame):
    """
    画面のヘッダー部
    """
    def __init__(self, master, controller: AppController, bg: str, icons_path: Path):
        super().__init__(master, bg=bg)
        self.controller = controller
        self.createWidgets(str(icons_path))

    def createWidgets(self, icons_path: str):
        self.btn_select_file = PhotoImageButton(self,
                                                image_path=str(Path(icons_path, "file_open_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                                command=self.controller.handle_select_files_event)
        self.btn_select_file.grid(row=0, column=0, padx=(0, 0))
        self.btn_back_file = PhotoImageButton(self, image_path=str(Path(icons_path, "arrow_back_24dp_FILL0_wght400_GRAD0_opsz24.png")))
        self.btn_back_file.grid(row=0, column=1, padx=(4, 0))
        self.btn_forward_file = PhotoImageButton(self, image_path=str(Path(icons_path, "arrow_forward_24dp_FILL0_wght400_GRAD0_opsz24.png")))
        self.btn_forward_file.grid(row=0, column=2, padx=(4, 0))
        self.widgetHeader = tk.Label(self, text="画面に画像ファイルをドラッグ＆ドロップしてください。", font=("", 10))
        self.widgetHeader.grid(row=0, column=3, padx=(4, 0))


class MainFrame(tk.Frame):
    """
    画面のメイン部
    """
    def __init__(self, master, bg):
        super().__init__(master, bg=bg)

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
        self.updateImage("")
        self.t = MosaicImageFile("")

    def updateImage(self, filepath):
        if len(filepath) == 0:
            return
        self.t = MosaicImageFile(filepath)

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
        # ドラッグ開始位置を記録（キャンバス上の座標に変換）
        self.start_x = int(self.canvas.canvasx(event.x))
        self.start_y = int(self.canvas.canvasy(event.y))

    def dragging(self, event):
        if self.photo is None:
            return
        # ドラッグ中は選択領域を表示
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        end_x = int(self.canvas.canvasx(event.x))
        end_y = int(self.canvas.canvasy(event.y))
        self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline='red', tags='dragging')

    def end_drag(self, event):
        # ドラッグ終了位置を取得（キャンバス上の座標に変換）
        end_x = int(self.canvas.canvasx(event.x))
        end_y = int(self.canvas.canvasy(event.y))

        # 選択領域にモザイクをかける
        self.apply_mosaic(self.start_x, self.start_y, end_x, end_y)

        # ドラッグ中に表示した選択領域を削除
        self.canvas.delete('dragging')

    def apply_mosaic(self, start_x, start_y, end_x, end_y):
        if self.photo is None:
            return

        mosaic = MosaicImage(self.original_image)
        #mosaic.cell_size = mosaic.calc_cell_size()
        print(mosaic.cell_size)
        mosaic.apply(start_x, start_y, end_x, end_y)
        self.original_image = mosaic.Image

        self.photo = ImageTk.PhotoImage(self.original_image)  # 元の画像のコピーをキャンバスに表示
        # キャンバスの画像も更新
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        new_filepath = self.t.newMosaicFile()
        mosaic.save(str(new_filepath))

        # キャンバスのスクロール領域を設定
        self.canvas.config(scrollregion=(0, 0, self.original_image.width, self.original_image.height))


class FooterFrame(tk.Frame):
    """
    画面のフッター部
    """
    def __init__(self, master, bg):
        super().__init__(master, bg=bg)
        self.createWidgets()

    def createWidgets(self):
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

    def updateStatus(self, filepath):
        target = MosaicImageFile(filepath)

        # 画像の幅と高さを取得
        with Image.open(filepath) as img:
            width, height = img.size

        # 画像の幅と高さを表示
        self.imageSizeBar.config(text=f"Width: {width}px, Height: {height}px")
        # ファイルサイズを取得
        filesize_kb = Decimal(target.st_size) / Decimal(1024)
        # ファイルサイズを表示
        self.fileSizeBar.config(text=str(round_up_decimal(Decimal(filesize_kb), 2)) + " KB")
        # 最終更新日時
        self.modified.config(text=target.mtime)
