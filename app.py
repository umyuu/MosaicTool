# -*- coding: utf-8 -*-
"""
    MosaicTool
"""
from argparse import ArgumentParser
from dataclasses import dataclass
from decimal import Decimal, ROUND_UP
from functools import partial
from pathlib import Path
import sys
import os
import time
import tkinter as tk
from tkinter import filedialog

from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk

from widgets.core import PhotoImageButton

PROGRAM_NAME = 'MosaicTool'
__version__ = '0.0.1'

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


@dataclass
class TargetFile:
    _file_path: str = ""
    # ファイルのメタデータを取得
    file_stat = Path(_file_path).stat()

    @property
    def mtime(self) -> str:
        # 最終更新日時を取得
        timestamp = self.file_stat.st_mtime
        # タイムスタンプをISO 8601形式に変換
        return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(timestamp))

    @property
    def st_size(self) -> int:
        return self.file_stat.st_size


class HeaderFrame(tk.Frame):
    def __init__(self, master, bg):
        super().__init__(master, bg=bg)
        self.createWidgets()

    def createWidgets(self):
        self.btn_select_file = PhotoImageButton(self, image_path=str(Path(icons_path, "file_open_24dp_FILL0_wght400_GRAD0_opsz24.png")), command=partial(self.on_select_file, event=None))
        self.btn_select_file.grid(row=0, column=0, padx=(0, 0))
        self.btn_back_file = PhotoImageButton(self, image_path=str(Path(icons_path, "arrow_back_24dp_FILL0_wght400_GRAD0_opsz24.png")), command=partial(self.on_select_file, event=None))
        self.btn_back_file.grid(row=0, column=1, padx=(4, 0))
        self.btn_forward_file = PhotoImageButton(self, image_path=str(Path(icons_path, "arrow_forward_24dp_FILL0_wght400_GRAD0_opsz24.png")), command=partial(self.on_select_file, event=None))
        self.btn_forward_file.grid(row=0, column=2, padx=(4, 0))
        self.widgetHeader = tk.Label(self, text="ヘッダーはここ", font=("", 10))
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
        self.canvas.image = None
        self.photo = None
        self.updateImage("")

    def updateImage(self, filepath):
        if len(filepath) == 0:
            return
        
        self.canvas.image = Image.open(filepath)
        self.photo = ImageTk.PhotoImage(self.canvas.image)

        # 画像を更新
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        # キャンバスのスクロール領域を設定
        self.canvas.config(scrollregion=(0, 0, self.canvas.image.width, self.canvas.image.height))

    def start_drag(self, event):
        # ドラッグ開始位置を記録
        self.start_x = event.x
        self.start_y = event.y

    def dragging(self, event):
        if self.photo is None:
            return
        # ドラッグ中は選択領域を表示
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline='red', tags='dragging')

    def end_drag(self, event):
        # ドラッグ終了位置を取得
        end_x = event.x
        end_y = event.y

        # 選択領域にモザイクをかける
        self.apply_mosaic(self.start_x, self.start_y, end_x, end_y)

        # ドラッグ中に表示した選択領域を削除
        self.canvas.delete('dragging')

    def apply_mosaic(self, start_x, start_y, end_x, end_y):
        if self.canvas.image is None:
            return

        # モザイクをかける領域を切り出す
        region = self.canvas.image.crop((start_x, start_y, end_x, end_y))

        # 切り出した領域を縮小し、元のサイズに拡大することでモザイクをかける
        region = region.resize((10, 10), Image.BOX).resize(region.size, Image.NEAREST)

        # モザイクをかけた領域を元の画像に戻す
        self.canvas.image.paste(region, (start_x, start_y, end_x, end_y))

        # 画像を更新
        self.photo = ImageTk.PhotoImage(self.canvas.image)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        # キャンバスのスクロール領域を設定
        self.canvas.config(scrollregion=(0, 0, self.canvas.image.width, self.canvas.image.height))


def round_up_decimal(value: Decimal):
    # 小数点以下2桁に切り上げ
    rounded_value = value.quantize(Decimal('0.01'), rounding=ROUND_UP)
    return rounded_value


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
        target = TargetFile(filepath)
        # ステータスバーに表示
        self.modified.config(text=target.mtime)
        # ファイルサイズを取得
        filesize_kb = Decimal(target.st_size) / 1024
        # ファイルサイズを表示
        self.fileSizeBar.config(text=str(round_up_decimal(filesize_kb)) + " KB")


class MainPage(tk.Frame):
    def __init__(self):
        super().__init__(bg="#00C8B4")
        self.HeaderFrame = HeaderFrame(self, bg="#44F7D3")
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
        message = '\n' + e.data
        self.MainFrame.updateImage(e.data)
        #text = self.MainFrame.textbox
        #text.configure(state='normal')
        #text.insert(tk.END, message)
        #text.configure(state='disabled')

        #text.see(tk.END)

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

        self.TargetFile = TargetFile()
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

        image = Image.open(e.data)
        #image.show()


if __name__ == "__main__":

    app = MyApp()
    end = time.time()
    print(f"\n起動時間({end - start:.3f}s)")
    app.mainloop()
