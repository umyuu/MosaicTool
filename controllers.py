# -*- coding: utf-8 -*-
"""
    MosaicTool
"""
from pathlib import Path

from lib.models import DataModel


class AppController:
    def __init__(self, model: DataModel, view):
        self.model = model
        self.view = view

    def add_file_path(self, file_path: str):
        path = Path(file_path)
        self.model.add_file_path(path)
        self.view.display_image(path)

    def addRange_file_path(self, files: tuple[str, ...]):
        for file_path in files:
            self.add_file_path(file_path)

    def handle_drop_event(self, event):
        self.model.clear()
        file_paths = event.data.split()  # 複数のパスを分割
        for file_path in file_paths:
            self.add_file_path(file_path)
            break
        self.view.FooterFrame.updateStatus(file_path)

    def handle_select_files_event(self):
        self.view.on_select_files(None)
