# -*- coding: utf-8 -*-
"""
    MosaicTool
"""
import asyncio
from src.utils import get_package_version, Stopwatch
sw = Stopwatch.start_new()

from functools import partial
from pathlib import Path
import sys
import os
import tkinter as tk

from tkinterdnd2 import TkinterDnD

from src.app_config import AppConfig
from src.controllers import AppController
from src.models import AppDataModel
from src.widgets import MainPage

PROGRAM_NAME = 'MosaicTool'
__version__ = get_package_version()


def get_application_path() -> Path:
    """アプリへのパスを取得する関数
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstallerから起動時は、カレントディレクトリのパスを取得します。
        base_path = Path.cwd()
    else:
        # 開発中のスクリプトのディレクトリ
        base_path = Path(__file__).resolve().parent

    return base_path


application_path = get_application_path()
# アイコンのパスを作成
icons_path = Path(os.path.dirname(os.path.abspath(__file__)), "third_party/icons")

# コマンドライン引数の解析
file_paths: list[str] = []
args = sys.argv[1:]
if not args:
    pass
else:
    file_paths = args

# 設定ファイルより
config_file = Path(application_path, f"{PROGRAM_NAME}.json")
config = AppConfig(config_file)


class MyApp(TkinterDnD.Tk):
    """
    アプリ
    アプリ全体でドラッグ＆ドロップを補足するために使用しています。
    """
    def __init__(self):
        super().__init__()
        self.set_window_title(Path(""))  # プログラム名とバージョン番号を表示
        self.model = AppDataModel(config)
        self.config = config
        width, height = config.get("window_sizes").get("main")
        self.geometry(f'{width}x{height}')  # ウィンドウサイズ

        self.controller = AppController(self.model, None, self.set_window_title)
        self.controller.icons_path = icons_path
        self.MainPage = MainPage(self, self.controller)

        self.MainPage.grid(column=0, row=0, sticky=tk.E + tk.W + tk.S + tk.N)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.controller.view = self.MainPage
        self.protocol('WM_DELETE_WINDOW', self.on_window_close)
        # 遅延してイベントループで処理をします。
        self.MainPage.after(1, partial(self.after_launch, file_paths))

    def on_window_close(self):
        """
        アプリのウィンドウを閉じる時に発生します。
        """
        try:
            if self.controller:
                self.controller.handle_auto_save(None)
        finally:
            self.destroy()  # ウィンドウを閉じる

    def set_window_title(self, filepath: Path):
        """
        ウィンドウタイトルを設定する
        :param filepath: 画像ファイルパス
        """
        filename = filepath.name if filepath else ""
        title = f"{filename} - {PROGRAM_NAME} {__version__}" if filename else f"{PROGRAM_NAME} {__version__}"
        self.title(title)

    def after_launch(self, files: list[str]):
        """
        プログラムを開始する。
        :param files: 起動時に渡されたファイル(送るメニューより)
        """
        # コマンドライン引数で渡されたファイルパスを処理する
        self.controller.handle_select_files_complete(files)
        self.controller.update_status_bar_file_info()
        self.controller.display_process_time(f"{sw.elapsed:.3f}s")


async def main():
    app = MyApp()
    app.mainloop()

if __name__ == "__main__":
    asyncio.run(main())
