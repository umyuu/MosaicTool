# -*- coding: utf-8 -*-
"""
    AbstractControllers
    循環importを防止するためのControllersの抽象クラスです。
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional

from . app_config import AppConfig, FontSize
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
    def handle_file_property(self, event=None):
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

    @property
    def font_sizes(self) -> FontSize:
        """
        フォントサイズを取得します。
        :return: フォントサイズ
        """
        raise NotImplementedError()

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

    @abstractmethod
    def get_config(self) -> AppConfig:
        pass

    @abstractmethod
    def set_file_property_visible(self, visible: bool):
        pass

    @abstractmethod
    def is_file_property_visible(self) -> bool:
        pass
