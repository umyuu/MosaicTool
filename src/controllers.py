# -*- coding: utf-8 -*-
"""
    AppController
"""
from pathlib import Path
from typing import Iterable

from . models import DataModel, StatusMessage, MosaicImageFile
from . image_file_service import ImageFileService
from . utils import Stopwatch


class AppController:
    """
    コントローラー
    """
    def __init__(self, model: DataModel, view, window_title_callback):
        self.model = model
        self.view = view
        self.window_title_callback = window_title_callback

    def add_file_path(self, file_path: Path) -> int:
        """
        ファイルをデータモデルに追加します。
        パスがディレクトリの場合は、ディレクトリ内のファイルも追加します。
        :return: 追加件数
        """
        if not file_path.is_dir():  # ファイルの場合
            return self.model.add_file_path(file_path)

        count: int = 0
        for f in file_path.glob("*.*"):  # ディレクトリの場合
            count += self.model.add_file_path(f)
        return count

    def handle_drop(self, event):
        """
        ドロップイベント
        """
        sw = Stopwatch.start_new()

        count: int = 0
        if not event.data:
            self.view.status_message("No data received in drop event")
            self.display_process_time(f"{sw.elapsed:.3f}s")
            return

        self.model.clear()
        file_paths = event.data.split('\n')  # 改行で分割
        for file_path in file_paths:
            for f in file_path.split():
                path = Path(f)
                if (path.exists()):
                    print(f"Processing file: {path}")
                    count += self.add_file_path(path)

        print(self.model)
        if count > 0:
            self.display_image()

        self.view.status_message(f"received in drop files:{count}")
        self.display_process_time(f"{sw.elapsed:.3f}s")

    def handle_file_open(self, event=None):
        """
        ファイル選択ボタンクリック時
        """
        self.view.on_select_files(None)

    def handle_save_as(self, event=None):
        """
        ファイルを選択して保存ボタンをクリック時
        """
        self.view.on_save_as(None)

    def handle_back_image(self, event=None):
        """
        前の画像に遷移するをクリック時
        """
        self.model.prev_index()
        self.display_image()

    def handle_forward_image(self, event=None):
        """
        次の画像に遷移するをクリック時
        """
        self.model.next_index()
        self.display_image()

    def handle_info_image(self, event=None):
        """
        画像情報を表示するをクリック時
        """
        file = self.model.get_current_file()
        d = ImageFileService.get_image_info(file)
        print(d)

    def display_image(self):
        """
        画面に画像を表示します。
        """
        file = self.model.get_current_file()
        self.view.display_image(file)

    def handle_select_files_complete(self, files: Iterable[str]):
        """
        ファイル選択ダイアログよりファイル選択時
        """
        count: int = 0
        total: int = 0
        self.model.clear()
        for file_path in files:
            count += self.add_file_path(Path(file_path))
            total += 1
        if count == 0:
            self.view.status_message("No image file")
            return

        self.display_image()
        self.view.status_message(f"select files:{count} / {total}")

    def get_mosaic_filename(self) -> Path:
        """
        モザイク適用後のファイル名を生成します。
        :return: Path
        """
        f = self.model.get_current_file()
        return ImageFileService.mosaic_filename(f)

    def set_window_title(self, text: Path):
        """
        タイトルバーの設定
        """
        self.window_title_callback(text)

    def display_process_time(self, time) -> None:
        """
        処理時間の設定
        """
        self.view.status_process_time(time)

    def get_status(self) -> StatusMessage:
        """
        ステータスメッセージを取得します。
        """
        files = self.model.get_file_paths()
        total = len(files)
        if total == 0:
            return StatusMessage()

        filepath = self.model.get_current_file()
        width, height = ImageFileService.get_image_size(filepath)

        m = MosaicImageFile(filepath)

        return StatusMessage(
            current=self.model.current + 1,
            total=total,
            mtime=m.mtime,
            file_size=m.st_size,
            width=width,
            height=height
        )
