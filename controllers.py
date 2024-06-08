# -*- coding: utf-8 -*-
"""
    AppController
"""
from pathlib import Path

from PIL import Image

from lib.models import DataModel, StatusMessage, MosaicImageFile


class AppController:
    def __init__(self, model: DataModel, view):
        self.model = model
        self.view = view

    def add_file_path(self, file_path: str):
        path = Path(file_path)
        self.model.add_file_path(path)

    def handle_drop(self, event):
        self.model.clear()
        file_paths = event.data.split()  # 複数のパスを分割
        for file_path in file_paths:
            self.add_file_path(file_path)

        self.display_image()

    def handle_pick_images(self):
        """
        ファイル選択ボタンクリック時
        """
        self.view.on_select_files(None)

    def handle_back_images(self):
        """
        前の画像に遷移するをクリック時
        """
        self.model.prev_index()
        self.display_image()

    def handle_forward_images(self):
        """
        次の画像に遷移するをクリック時
        """
        self.model.next_index()
        self.display_image()

    def display_image(self):
        """
        画面に画像を表示します。
        """
        file = self.model.get_current_file()
        self.view.display_image(file)

    def handle_select_files_complete(self, files: tuple[str, ...]):
        """
        ファイル選択ダイアログよりファイル選択時
        """
        self.model.clear()
        for file_path in files:
            self.add_file_path(file_path)

        self.display_image()

    def get_status(self) -> StatusMessage:
        """
        ステータスメッセージを取得します。
        """
        files = self.model.get_file_paths()
        total = len(files)        
        if total == 0:
            return StatusMessage()

        filepath = files[0]
        with Image.open(filepath) as img:
            width, height = img.size

        m = MosaicImageFile(str(filepath))

        return StatusMessage(
            current=self.model.current + 1,
            total=total,
            mtime=m.mtime,
            file_size=m.st_size,
            width=width,
            height=height
        )
