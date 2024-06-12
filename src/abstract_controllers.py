# -*- coding: utf-8 -*-
"""
    AbstractControllers
    循環importを防止するためのControllersの抽象クラスです。
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional

from . models import AppDataModel, StatusBarInfo
from . utils import Stopwatch


class AbstractAppController(ABC):
    """
    AppControllerの抽象クラス
    """
    def __init__(self, model: AppDataModel, view, window_title_callback):
        pass
        #self.model = model
        #self.view = view
        #self.window_title_callback = window_title_callback
        # ドラッグ＆ドロップで渡されたパスを分割する正規表現
        #self.drop_file_split = re.compile(r'([A-Za-z]:[/|\\\\].*?(?=[A-Za-z]:[/|\\\\]|$))', re.RegexFlag.UNICODE)
        #self.image_controller = ImageController(self)

    @abstractmethod
    def add_file_path(self, item) -> int:
        pass

    @abstractmethod
    def get_current_image(self) -> Path:
        pass

    @abstractmethod
    def handle_drop(self, event):
        pass

    @abstractmethod
    def handle_file_open(self, event=None):
        pass

    @abstractmethod
    def handle_save_as(self, event=None):
        pass

    @abstractmethod
    def handle_back_image(self, event=None):
        pass

    @abstractmethod
    def handle_forward_image(self, event=None):
        pass

    @abstractmethod
    def handle_info_image(self, event=None):
        pass

    @abstractmethod
    def update_view(self, sw: Optional[Stopwatch] = None):
        pass

    @abstractmethod
    def update_status_bar_file_info(self):
        pass

    @abstractmethod
    def handle_select_files_complete(self, files: Iterable[str]):
        pass

    @abstractmethod
    def get_mosaic_filename(self) -> Path:
        pass

    @abstractmethod
    def set_window_title(self, text: Path):
        pass

    @abstractmethod
    def display_process_time(self, time: str) -> None:
        pass

    @abstractmethod
    def get_status(self) -> StatusBarInfo:
        pass

    @abstractmethod
    def get_view(self):
        pass
