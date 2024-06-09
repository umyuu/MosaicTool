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

from tkinterdnd2 import DND_FILES, TkinterDnD

from lib.models import MosaicImageFile, DataModel
from lib.utils import get_package_version
from controllers import AppController
from widgets import HeaderFrame, MainFrame, FooterFrame, MainPage


PROGRAM_NAME = 'MosaicTool'
__version__ = get_package_version()

start = time.time()
application_path = os.path.dirname(os.path.abspath(__file__))
# アイコンのパスを作成
icons_path = Path(application_path, "third_party/icons")

# コマンドライン引数の解析
file_paths: list[str] = []
args = sys.argv[1:]
if not args:
    pass
else:
    file_paths = args


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
        #self.set_window_title("")  # プログラム名とバージョン番号を表示
        self.model = DataModel()
        self.controller = AppController(self.model, None, self.set_window_title)
        self.MainPage = MainPage(self, self.controller, icons_path)
        self.set_window_title("")
        self.MainPage.grid(column=0, row=0, sticky=tk.E + tk.W + tk.S + tk.N)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.controller.view = self.MainPage  # コントローラーにビューを設定
        self.MainPage.after(1, partial(self.controller.handle_select_files_complete, file_paths))

    def set_window_title(self, filepath):
        filename = Path(filepath).name if filepath else ""
        title = f"{filename} - {PROGRAM_NAME} {__version__}" if filename else f"{PROGRAM_NAME} {__version__}"
        self.title(title)


if __name__ == "__main__":
    app = MyApp()
    end = time.time()
    print(f"\n起動時間({end - start:.3f}s)")
    app.mainloop()
