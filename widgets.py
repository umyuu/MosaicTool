# -*- coding: utf-8 -*-
"""
    PhotoImageButton
"""
from decimal import Decimal
from functools import partial
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

from lib.models import MosaicImageFile
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
    def __init__(self, master, bg: str, icons_path: Path):
        super().__init__(master, bg=bg)
        self.createWidgets(str(icons_path))

    def createWidgets(self, icons_path: str):
        self.btn_select_file = PhotoImageButton(self, image_path=str(Path(icons_path, "file_open_24dp_FILL0_wght400_GRAD0_opsz24.png")), command=partial(self.on_select_file, event=None))
        self.btn_select_file.grid(row=0, column=0, padx=(0, 0))
        self.btn_back_file = PhotoImageButton(self, image_path=str(Path(icons_path, "arrow_back_24dp_FILL0_wght400_GRAD0_opsz24.png")), command=partial(self.on_select_file, event=None))
        self.btn_back_file.grid(row=0, column=1, padx=(4, 0))
        self.btn_forward_file = PhotoImageButton(self, image_path=str(Path(icons_path, "arrow_forward_24dp_FILL0_wght400_GRAD0_opsz24.png")), command=partial(self.on_select_file, event=None))
        self.btn_forward_file.grid(row=0, column=2, padx=(4, 0))
        self.widgetHeader = tk.Label(self, text="画面に画像ファイルをドラッグ＆ドロップしてください。", font=("", 10))
        self.widgetHeader.grid(row=0, column=3, padx=(4, 0))

    def on_select_file(self, event):
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
        print('on_select_file...')
        return filedialog.askopenfilename(parent=self, filetypes=IMAGE_FILE_TYPES)


class FooterFrame(tk.Frame):
    def __init__(self, master, bg):
        super().__init__(master, bg=bg)
        self.createWidgets()

    def createWidgets(self):
        self.modified = tk.Label(self, text=" " * 20, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.modified.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.fileSizeBar = tk.Label(self, text=" " * 20, bd=1, relief=tk.SUNKEN, anchor=tk.W)  # ファイルサイズ表示用のラベルを追加
        self.fileSizeBar.grid(row=0, column=1, sticky=tk.W + tk.E)
        self.paddingLabel = tk.Label(self, text="フッターはここ")  # 余白調整用のラベルを追加
        self.paddingLabel.grid(row=0, column=2, sticky=tk.W + tk.E)  # stickyをW+Eに変更
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)  # 列2（余白調整用のラベル）にweightを設定

    def updateStatus(self, filepath):
        target = MosaicImageFile(filepath)
        # ステータスバーに表示
        self.modified.config(text=target.mtime)
        # ファイルサイズを取得
        filesize_kb = Decimal(target.st_size) / 1024
        # ファイルサイズを表示
        self.fileSizeBar.config(text=str(round_up_decimal(Decimal(filesize_kb), 2)) + " KB")
