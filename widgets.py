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

from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

from controllers import AppController
from src.models import MosaicFilter, StatusMessage, ImageFormat
from src.utils import round_up_decimal
from src.widgets_core import WidgetUtils, PhotoImageButton, Tooltip
from src.image_file_service import ImageFileService

PROGRAM_NAME = 'MosaicTool'


class HeaderFrame(tk.Frame):
    """
    画面のヘッダー部
    """
    def __init__(self, master, controller: AppController, bg: str, icons_path: Path):
        super().__init__(master, bg=bg)

        self.controller = controller
        self.btn_file_open = PhotoImageButton(self,
                                              image_path=str(Path(icons_path, "file_open_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                              tooltip_text="Open (Ctrl+O)",
                                              command=self.controller.handle_file_open)
        WidgetUtils.bind_all(self, "Control", "O", partial(self.controller.handle_file_open))
        self.btn_file_open.grid(row=0, column=0, padx=(0, 0))

        self.btn_save_as = PhotoImageButton(self,
                                            image_path=str(Path(icons_path, "save_as_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                            tooltip_text="SaveAs (Ctrl+Shift+S)",
                                            command=self.controller.handle_save_as)
        WidgetUtils.bind_all(self, "Control-Shift", "S", partial(self.controller.handle_save_as))
        self.btn_save_as.grid(row=0, column=1, padx=(4, 0))

        self.btn_back = PhotoImageButton(self,
                                         image_path=str(Path(icons_path, "arrow_back_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                         tooltip_text="Previous file (<-)",
                                         command=self.controller.handle_back_image)
        WidgetUtils.bind_all(self, "", "Left", partial(self.controller.handle_back_image))
        WidgetUtils.bind_all(self, "Shift", "Left", partial(self.controller.handle_back_image))
        self.btn_back.grid(row=0, column=2, padx=(4, 0))

        self.btn_forward = PhotoImageButton(self,
                                            image_path=str(Path(icons_path, "arrow_forward_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                            tooltip_text="Next file (->)",
                                            command=self.controller.handle_forward_image)
        WidgetUtils.bind_all(self, "", "Right", partial(self.controller.handle_forward_image))
        WidgetUtils.bind_all(self, "Shift", "Right", partial(self.controller.handle_forward_image))
        self.btn_forward.grid(row=0, column=3, padx=(4, 0))

        self.btn_info_file = PhotoImageButton(self,
                                              image_path=str(Path(icons_path, "info_24dp_FILL0_wght400_GRAD0_opsz24.png")),
                                              tooltip_text="Image Information (I)",
                                              command=self.controller.handle_info_image)
        WidgetUtils.bind_all(self, "", "I", partial(self.controller.handle_info_image))
        self.btn_info_file.grid(row=0, column=4, padx=(4, 0))

        self.widgetHeader = tk.Label(self, text="画面に画像ファイルをドラッグ＆ドロップしてください。", font=("", 14))
        self.widgetHeader.grid(row=0, column=5, padx=(4, 0))


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

        self.photo = None
        self.start_x = 0
        self.start_y = 0
        #self.rect_tag: Optional[int] = None  # 矩形のタグ
        #self.size_label = None  # サイズ表示用ラベル
        self.rect_tag = None  # 矩形のタグ
        self.size_label = None  # サイズ表示用ラベル
        # ドラッグ開始時のイベントをバインド
        self.canvas.bind("<Button-1>", self.start_drag)

        # ドラッグ中のイベントをバインド
        self.canvas.bind("<B1-Motion>", self.dragging)

        # ドラッグ終了時のイベントをバインド
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

    def updateImage(self, filepath: Path):
        if not filepath.exists():
            return

        self.original_image = ImageFileService.load(filepath)  # 元の画像を開く
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
        #if self.photo is None:
        #    return

        end_x = int(self.canvas.canvasx(event.x))
        end_y = int(self.canvas.canvasy(event.y))

        # 矩形が既に存在する場合は削除する
        if self.rect_tag:
            self.canvas.delete(self.rect_tag)
        if self.size_label:
            self.canvas.delete(self.size_label)

        # 矩形を描画し、タグを付ける
        self.rect_tag = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline='red')

        # サイズを計算して表示
        width = abs(end_x - self.start_x)
        height = abs(end_y - self.start_y)

        # サイズラベルの位置をマウスカーソルの近くに設定
        label_x = end_x + 10
        label_y = end_y + 10
        self.size_label = self.canvas.create_text((label_x, label_y), font=("", 12), text=f"{width} x {height}", anchor="nw")

    def end_drag(self, event):
        """
        ドラッグ終了時
        """
        try:
            # ドラッグ終了位置を取得（キャンバス上の座標に変換）
            end_x = int(self.canvas.canvasx(event.x))
            end_y = int(self.canvas.canvasy(event.y))

            # 選択領域にモザイクをかける
            self.apply_mosaic(self.start_x, self.start_y, end_x, end_y)
        except Exception as e:
            print(f"Error applying mosaic: {e}")
            raise e
        finally:
            # 矩形とサイズ表示用ラベルを削除
            if self.rect_tag:
                self.canvas.delete(self.rect_tag)
            if self.size_label:
                self.canvas.delete(self.size_label)

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

        # モザイク適用後のファイルを自動保存します。
        self.save(self.controller.get_mosaic_filename())

    def save(self, output_path: Path, override: bool = False):
        """
        モザイク画像を保存する
        :param output_path: 保存するファイルの名前
        :param override: 自動保存時に上書きするかの確認
        """
        current_file = self.controller.model.get_current_file()

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

        self.imageSizeBar = tk.Label(self, text=" ", bd=1, relief=tk.SUNKEN, anchor=tk.W)  # 画像サイズ表示用のラベルを追加
        self.imageSizeBar.tooltip = Tooltip(self.imageSizeBar, "Width x Height")
        self.imageSizeBar.grid(row=0, column=0, sticky=tk.W + tk.E)

        self.count = tk.Label(self, text="  1 /  1 ", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.count.tooltip = Tooltip(self.count, "Current / Total")
        self.count.grid(row=0, column=1, sticky=tk.W + tk.E)

        self.fileSizeBar = tk.Label(self, text=" ", bd=1, relief=tk.SUNKEN, anchor=tk.W)  # ファイルサイズ表示用のラベルを追加
        self.fileSizeBar.tooltip = Tooltip(self.fileSizeBar, "File Size")
        self.fileSizeBar.grid(row=0, column=2, sticky=tk.W + tk.E)

        self.modified = tk.Label(self, text=" ", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.modified.tooltip = Tooltip(self.modified, "モザイク加工対象ファイルの最終更新日時")
        self.modified.grid(row=0, column=3, sticky=tk.W + tk.E)

        self.paddingLabel = tk.Label(self, text="フッターはここ", anchor="e")  # 余白調整用のラベルを追加
        self.paddingLabel.grid(row=0, column=4, sticky=tk.W + tk.E)

        self.columnconfigure(0, weight=1, minsize=56)
        self.columnconfigure(1, weight=1, minsize=40)
        self.columnconfigure(2, weight=1, minsize=48)
        self.columnconfigure(3, weight=1, minsize=64)
        self.columnconfigure(4, weight=1, minsize=480)  # 列2（余白調整用のラベル）にweightを設定

    def updateStatusBar(self, status: StatusMessage):
        """
        ステータスバーを更新します。
        """
        # 画像の幅と高さ
        self.imageSizeBar.config(text=f"{status.width} x {status.height}")
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
        self.MainFrame.updateImage(path)
        self.controller.set_window_title(path)
        self.updateFileStatus()

    def on_select_files(self, event):
        """
        ファイル選択ボタン
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

    def on_save_as(self, event):
        """
        ファイルを選択して保存ボタン
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
            self.on_save_as(event)
            return

        self.MainFrame.save(save_file, True)

        messagebox.showinfo(PROGRAM_NAME, f"ファイルを保存しました。\n\n{save_file}")
        self.status_message(f"ファイルを保存しました。{save_file}")

    def updateFileStatus(self):
        """
        フッターのステータスバーを更新
        """
        self.FooterFrame.updateStatusBar(self.controller.get_status())

    def status_message(self, text: str):
        """
        フッターのステータスバーのメッセージ欄
        """
        self.FooterFrame.updateMessage(text)
