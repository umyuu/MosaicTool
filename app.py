# -*- coding: utf-8 -*-
"""
    MosaicTool
"""
from functools import partial
from pathlib import Path
import sys
import os
import json
import tkinter as tk

from tkinterdnd2 import TkinterDnD

from src.models import DataModel
from src.utils import get_package_version, Stopwatch
from controllers import AppController
from widgets import MainPage


PROGRAM_NAME = 'MosaicTool'
__version__ = get_package_version()
sw = Stopwatch.start_new()

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

# 設定ファイルより
config_file = Path(application_path, f"{PROGRAM_NAME}.json")
if config_file.exists():
    with config_file.open(encoding='utf-8') as f:
        config = json.load(f)
else:
    config = {}


class MyApp(TkinterDnD.Tk):
    """
    アプリ
    アプリ全体でドラッグ＆ドロップを補足するために使用しています。
    """
    def __init__(self):
        super().__init__()
        initial_window_size = config.get("initialWindowSize", {"width": 800, "height": 600})
        width = initial_window_size.get("width")
        height = initial_window_size.get("height")
        self.geometry(f'{width}x{height}')  # ウィンドウサイズ
        self.minsize(width, height)
        self.set_window_title(Path(""))  # プログラム名とバージョン番号を表示

        self.model = DataModel()
        self.controller = AppController(self.model, None, self.set_window_title)
        self.MainPage = MainPage(self, self.controller, icons_path)
        self.MainPage.grid(column=0, row=0, sticky=tk.E + tk.W + tk.S + tk.N)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.controller.view = self.MainPage  # コントローラーにビューを設定
        # 遅延してイベントループで処理をします。
        self.MainPage.after(1, partial(self.after_launch))

    def set_window_title(self, filepath: Path):
        filename = filepath.name if filepath else ""
        title = f"{filename} - {PROGRAM_NAME} {__version__}" if filename else f"{PROGRAM_NAME} {__version__}"
        self.title(title)

    def after_launch(self):
        """
        プログラムを開始します。
        """
        # コマンドライン引数で渡されたファイルパスを処理する
        self.controller.handle_select_files_complete(file_paths)
        self.MainPage.updateFileStatus()
        self.MainPage.status_message("起動時間")
        self.controller.on_file_save(f"{sw.elapsed:.3f}s")


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
