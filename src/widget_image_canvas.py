# -*- coding: utf-8 -*-
"""
    ImageCanvas
    画像を表示および編集するためのキャンバス
"""
import asyncio
import tkinter as tk
from tkinter import messagebox
from threading import Thread
from typing import Optional
from pathlib import Path

from PIL import ImageTk

from . import PROGRAM_NAME
from . abstract_controllers import AbstractAppController
from . utils import Stopwatch
from . image_file_service import ImageFileService
from . effects.image_effects import MosaicEffect


class ImageCanvas(tk.Frame):
    """
    画面のキャンバス領域
    """
    def __init__(self, master, controller: AbstractAppController):
        """
        コンストラクタ
        :param master: 親Widget
        :param controller: コントローラー
        :param bg: 背景色
        """
        super().__init__(master, bg=controller.theme_colors.bg_neutral)

        self.controller = controller
        font_sizes = self.controller.font_sizes
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

        # アプリ起動時の初期メッセージ。
        self.startup_message_id: Optional[int] = self.canvas.create_text(
            (0, 0),
            text="画面にフォルダまたはファイルをドラッグ＆ドロップしてください。",
            font=("", font_sizes.h4))

        self.photo_image: Optional[ImageTk.PhotoImage] = None
        # モザイク領域の選択開始位置
        self.start_x: int = 0
        self.start_y: int = 0
        self.rect_id: Optional[int] = None  # モザイクを指定した範囲の矩形
        self.size_label_id: Optional[int] = None  # サイズ表示用ラベル

        # ドラッグ開始時のイベントをバインド
        self.canvas.bind("<Button-1>", self.handle_start_drag)
        # ドラッグ中のイベントをバインド
        self.canvas.bind("<B1-Motion>", self.handle_dragging)
        # ドラッグ終了時のイベントをバインド
        self.canvas.bind("<ButtonRelease-1>", self.handle_end_drag)

        # 右クリックのイベントをバインド
        self.canvas.bind("<Button-3>", self.handle_right_click)
        # Shift+右クリックのイベントをバインド
        self.canvas.bind("<Shift-Button-3>", self.handle_shift_right_click)

        # ウィンドウサイズ変更時にキャンバスをリサイズする
        # リサイズイベントのunbind用にresize_handler_idにイベント関数を退避します。
        self.resize_handler_id: Optional[str] = self.canvas.bind("<Configure>", self.on_resize)

    # スクロールのバインド関数を追加
    def on_mousewheel(self, event):
        """
        マウスホイールイベント
        縦スクロールを行います。
        """
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_shift_mousewheel(self, event):
        """
        Shiftマウスホイールイベント
        横スクロールを行います。
        """
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_resize(self, event):
        """
        リサイズイベント
        初期表示メッセージの位置調整を行います。
        :param event: イベント
        """
        if self.startup_message_id is None:
            return
        # キャンバスの新しい幅と高さを取得
        canvas_width = event.width
        canvas_height = event.height

        # テキストの位置をキャンバスの中央に更新
        self.canvas.coords(self.startup_message_id, canvas_width / 2, canvas_height / 2)

    def suppress_startup_message(self):
        """
        スタートアップメッセージを非表示にします。
        """
        if self.resize_handler_id is None:
            return  # リサイズイベントが解除済み
        # 登録したリサイズイベントの解除
        self.canvas.unbind("<Configure>", self.resize_handler_id)
        self.resize_handler_id = None

        if self.startup_message_id is not None:
            self.canvas.delete(self.startup_message_id)
            self.startup_message_id = None

        # 画像を表示時は、マウスホイールスクロール操作を行えるようにします。
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self.on_shift_mousewheel)

    def handle_right_click(self, event):
        """
        右クリックの処理
        :param event: イベント
        """
        self.controller.handle_next_effect()

    def handle_shift_right_click(self, event):
        """
        Shift+右クリックの処理
        :param event: イベント
        """
        self.controller.handle_back_effect()

    def update_view(self, file_path: Path):
        """
        画面を更新します。
        :param file_path: 画像ファイルパス
        """
        if file_path is None:
            return
        self.suppress_startup_message()
        self.update_image(file_path)

    def update_image(self, file_path: Path):
        """
        表示画像を更新します。
        :param file_path: 画像ファイルパス
        """
        if not file_path.exists():
            return
        self.original_image = ImageFileService.load(file_path)  # 元の画像を開く
        self.photo_image = ImageTk.PhotoImage(self.original_image)  # 元の画像のコピーをキャンバスに表示
        # 画像を更新
        self.canvas_image = self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW)
        # キャンバスのスクロール領域を設定
        self.canvas.config(scrollregion=(0, 0, self.original_image.width, self.original_image.height))

    def handle_start_drag(self, event):
        """
        ドラッグ開始
        :param event: イベント
        """
        # ドラッグ開始位置を記録（キャンバス上の座標に変換）
        self.start_x = int(self.canvas.canvasx(event.x))
        self.start_y = int(self.canvas.canvasy(event.y))

    def handle_dragging(self, event):
        """
        ドラッグ中
        :param event: イベント
        """
        end_x = int(self.canvas.canvasx(event.x))
        end_y = int(self.canvas.canvasy(event.y))

        # 矩形が既に存在する場合は削除します。
        if self.rect_id is not None:
            self.canvas.delete(self.rect_id)
        if self.size_label_id is not None:
            self.canvas.delete(self.size_label_id)

        # 矩形を描画し、タグを付けます。
        self.rect_id: Optional[int] = self.canvas.create_rectangle(
            self.start_x, self.start_y, end_x, end_y,
            outline=self.controller.theme_colors.bg_danger)

        # サイズを計算して表示します。
        width = abs(end_x - self.start_x)
        height = abs(end_y - self.start_y)

        # サイズラベルの位置をマウスカーソルの近くに設定します。
        label_x = end_x + 10
        label_y = end_y + 10

        self.size_label_id: Optional[int] = self.canvas.create_text(
            (label_x, label_y),
            font=("", self.controller.font_sizes.h5), text=f"{width} x {height}",
            anchor="nw")

    def handle_end_drag(self, event):
        """
        ドラッグ終了時
        :param event: イベント
        """
        try:
            sw = Stopwatch.start_new()
            # ドラッグ終了位置を取得します。（キャンバス上の座標に変換）
            end_x = int(self.canvas.canvasx(event.x))
            end_y = int(self.canvas.canvasy(event.y))

            # 選択領域にモザイクをかけます。
            is_apply = self.apply_mosaic(self.start_x, self.start_y, end_x, end_y)
            if is_apply:
                self.controller.display_process_time(f"{sw.elapsed:.3f}s")
        except Exception as e:
            print(f"Error applying mosaic: {e}")
            raise e
        finally:
            # 矩形とサイズ表示用ラベルを削除
            if self.rect_id is not None:
                self.canvas.delete(self.rect_id)
            if self.size_label_id is not None:
                self.canvas.delete(self.size_label_id)

    def apply_mosaic(self, start_x: int, start_y: int, end_x: int, end_y: int) -> bool:
        """
        モザイクを適用します。
        :param start_x: モザイクをかける領域の左上X座標
        :param start_y: モザイクをかける領域の左上Y座標
        :param end_x: モザイクをかける領域の右下X座標
        :param end_y: モザイクをかける領域の右下Y座標
        :return: モザイクを掛けてたかどうか
        """
        if self.photo_image is None:
            return False  # 画像ファイルを未選択状態にモザイク領域を指定した時

        # 座標を正しい順序に並べ替える
        left = min(start_x, end_x)
        right = max(start_x, end_x)
        top = min(start_y, end_y)
        bottom = max(start_y, end_y)

        mosaic = self.controller.current_effect
        # Todo:mosaic#apply側で判定します。
        if mosaic.cell_size == MosaicEffect.AUTO:  # セルサイズの自動計算
            mosaic = MosaicEffect(MosaicEffect.calc_cell_size(self.original_image))
        is_apply = mosaic.apply(self.original_image, left, top, right, bottom)
        if not is_apply:
            return False

        self.photo_image = ImageTk.PhotoImage(self.original_image)  # 元の画像のコピーをキャンバスに表示
        # キャンバスの画像も更新※画像サイズを変更しないため、スクロール領域は更新しません。
        self.canvas.itemconfig(self.canvas_image, image=self.photo_image)
        # 変更状態に設定します。
        self.controller.update_data_state("Modified")

        return True

    def save(self, output_path: Path, override: bool = False):
        """
        モザイク画像を保存します。
        :param output_path: 保存するファイルの名前
        :param override: ファイル名を付けて保存時は、true、自動保存時は、false
        """
        current_file = self.controller.get_current_image()

        # 自動保存時に同一ファイル名の場合は、念のため確認メッセージを表示します。
        if not override:
            if current_file == output_path:
                retval = messagebox.askokcancel(
                    PROGRAM_NAME,
                    f"{output_path}は既に存在します。\n上書きしますか？")
                if not retval:
                    # ToDo: 自動保存時に同一ファイル名のエラー時の処理フローを改善する。
                    self.controller.update_data_state("Unchanged")
                    return
        # 未編集状態に戻します。
        self.controller.update_data_state("Unchanged")

        # 画像データをbytesに変換後、スレッドを起動します。
        mode = self.original_image.mode
        size = self.original_image.size
        data = self.original_image.tobytes()
        thread = Thread(target=lambda: asyncio.run(
            ImageFileService.save_async(mode, size, data, output_path, current_file)))
        thread.start()
