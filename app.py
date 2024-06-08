# -*- coding: utf-8 -*-
"""
    MosaicTool
"""
from argparse import ArgumentParser
from functools import partial
from pathlib import Path
import sys
import os
import time
import tkinter as tk
from tkinter import filedialog

from tkinterdnd2 import DND_FILES, TkinterDnD

from lib.models import MosaicImageFile
from lib.utils import get_package_version
from widgets import HeaderFrame, MainFrame, FooterFrame


PROGRAM_NAME = 'MosaicTool'
__version__ = get_package_version()

start = time.time()
application_path = os.path.dirname(os.path.abspath(__file__))
# アイコンのパスを作成
icons_path = Path(application_path, "third_party/icons")


parser = ArgumentParser(description="Process some files or directories.", add_help=False)

# コマンドライン引数を追加
parser.add_argument('-p', '--paths', metavar='path', type=str, nargs='+',
                    help='a path to a file or directory')

# 引数を解析
args = parser.parse_args()
if args.paths is not None:
    for path in args.paths:
        print(f"引数: {path}")


class MainPage(tk.Frame):
    def __init__(self):
        super().__init__(bg="#00C8B4")
        self.HeaderFrame = HeaderFrame(self, "#44F7D3", icons_path)
        self.HeaderFrame.grid(column=0, row=0, sticky=(tk.E + tk.W + tk.S + tk.N))
        self.MainFrame = MainFrame(self, bg="#88FFEB")
        self.MainFrame.grid(column=0, row=1, sticky=(tk.E + tk.W + tk.S + tk.N))
        self.FooterFrame = FooterFrame(self, bg="#FFBB9D")
        self.FooterFrame.grid(column=0, row=2, sticky=(tk.E + tk.W + tk.S + tk.N))

        # ヘッダーとフッターの行のweightを0に設定（固定領域）
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(2, weight=0)

        # メインフレームの行のweightを1に設定（残りのスペースをすべて取る）
        self.grid_rowconfigure(1, weight=1)

        self.columnconfigure(0, weight=1)  # ヘッダーをウィンドウ幅まで拡張する

    def pickImage(self, data: str):
        """
        画像ファイルを選択時
        """
        self.MainFrame.updateImage(data)
        # フッターのステータスバーを更新
        self.FooterFrame.updateStatus(data)

class MyApp(TkinterDnD.Tk):
    """
    アプリ
    アプリ全体でドラッグ＆ドロップを補足するために使用しています。
    """
    def __init__(self):
        super().__init__()

        width = 640
        height = 480
        self.geometry(f'{width}x{height}')  # ウィンドウサイズ
        self.minsize(width, height)
        self.set_window_title("")  # プログラム名とバージョン番号を表示

        self.TargetFile = MosaicImageFile()
        self.MainPage = MainPage()
        # ドラッグアンドドロップ
        self.MainPage.drop_target_register(DND_FILES)
        self.MainPage.dnd_bind('<<Drop>>', self.onDragAndDrop)
        # ファイル選択時
        self.MainPage.HeaderFrame.btn_select_file.configure(command=partial(self.on_select_file, event=None))
        self.MainPage.grid(column=0, row=0, sticky=tk.E + tk.W + tk.S + tk.N)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def set_window_title(self, filepath: str):
        """
        タイトルバーの設定
        """
        filename = Path(filepath).name if filepath else ""
        title = f"{filename} - {PROGRAM_NAME} {__version__}" if filename else f"{PROGRAM_NAME} {__version__}"
        self.title(title)

    def onDragAndDrop(self, e):
        """
        ドラッグ＆ドロップイベント
        """
        self.set_window_title(e.data)
        self.MainPage.pickImage(e.data)

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

        files = filedialog.askopenfilenames(parent=self, filetypes=IMAGE_FILE_TYPES)
        if files is None:
            return

        f = files[0]
        self.set_window_title(f)
        self.MainPage.pickImage(f)


if __name__ == "__main__":

    app = MyApp()
    end = time.time()
    print(f"\n起動時間({end - start:.3f}s)")
    app.mainloop()
