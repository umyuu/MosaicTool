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
        self.view.display_image(path)

    def handle_drop(self, event):
        self.model.clear()
        file_paths = event.data.split()  # 複数のパスを分割
        for file_path in file_paths:
            self.add_file_path(file_path)
            break
        self.view.FooterFrame.updateStatus2(self.get_status())

    def handle_pick_images(self):
        """
        ファイル選択ボタンクリック時
        """
        self.view.on_select_files(None)

    def handle_select_files_complete(self, files: tuple[str, ...]):
        """
        ファイル選択ダイアログよりファイル選択時
        """
        self.model.clear()
        for file_path in files:
            self.add_file_path(file_path)

    def get_status(self) -> StatusMessage:
        files = self.model.get_file_paths()
        filepath = files[0]
        with Image.open(filepath) as img:
            width, height = img.size

        m = MosaicImageFile(str(filepath))

        message = StatusMessage(
            current=1,
            total=len(files),
            mtime=m.mtime,
            file_size=m.st_size,
            width=width,
            height=height
        )

        return message
