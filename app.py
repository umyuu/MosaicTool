# -*- coding: utf-8 -*-
"""
    MosaicTool
"""
from argparse import ArgumentParser
from pathlib import Path
import sys
import os
import time
import tkinter as tk

from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk

from lib.models import MosaicImageFile, MosaicImage
from lib.utils import get_package_version
from widgets import HeaderFrame, FooterFrame


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


class MainFrame(tk.Frame):
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

        self.original_image = Image.open(filepath)  # 元の画像を開く
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
        mosaic.cell_size = mosaic.calc_cell_size()
        mosaic.apply(start_x, start_y, end_x, end_y)
        self.original_image = mosaic.Image

        self.photo = ImageTk.PhotoImage(self.original_image)  # 元の画像のコピーをキャンバスに表示
        # キャンバスの画像も更新
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        new_filepath = self.t.newMosaicFile()
        mosaic.save(str(new_filepath))

        # キャンバスのスクロール領域を設定
        self.canvas.config(scrollregion=(0, 0, self.original_image.width, self.original_image.height))


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

    def onUpdate(self, e):
        self.MainFrame.updateImage(e.data)
        # フッターのステータスバーを更新
        self.FooterFrame.updateStatus(e.data)


class MyApp(TkinterDnD.Tk):
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
        #self.MainPage.pack(expand=True)
        self.MainPage.grid(column=0, row=0, sticky=tk.E + tk.W + tk.S + tk.N)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def set_window_title(self, filepath: str):
        filename = Path(filepath).name if filepath else ""
        title = f"{filename} - {PROGRAM_NAME} {__version__}" if filename else f"{PROGRAM_NAME} {__version__}"
        self.title(title)

    def onDragAndDrop(self, e):
        """
        ドラッグ＆ドロップイベント
        """
        self.set_window_title(e.data)
        self.MainPage.onUpdate(e)


if __name__ == "__main__":

    app = MyApp()
    end = time.time()
    print(f"\n起動時間({end - start:.3f}s)")
    app.mainloop()
