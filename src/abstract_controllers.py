# -*- coding: utf-8 -*-
"""
    AbstractControllers
    循環importを防止するためのControllersの抽象クラスです。
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional, Literal

from . models import AppDataModel, StatusBarInfo
from . utils import Stopwatch


class AbstractAppController(ABC):
    """
    AppControllerの抽象クラス
    """
    def __init__(self, model: AppDataModel, view, window_title_callback):
        """
        コンストラクタ
        """
        pass

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
    def get_font_size(self, heading: Literal["h1", "h2", "h3", "h4", "h5"]) -> int:
        """
        指定した要素（見出しや本文）のフォントサイズを取得するメソッドです。
        :param element: 見出しの種類（'h1', 'h2', 'h3', 'h4', 'h5'）または 'body'（本文）
        :return: フォントサイズ
        """
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
