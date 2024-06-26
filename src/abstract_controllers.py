# -*- coding: utf-8 -*-
"""
    AbstractControllers
    循環importを防止するためのControllersの抽象クラスです。
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional

from . app_config import AppConfig, FontSize, ThemeColors
from . models import AppDataModel, StatusBarInfo, DATA_STATE
from . utils import Stopwatch
from . effects.image_effects import MosaicEffect


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
    def on_file_open(self, event=None):
        pass

    @abstractmethod
    def on_save_as(self, event=None):
        pass

    @abstractmethod
    def handle_back_image(self, event=None):
        pass

    @abstractmethod
    def handle_next_image(self, event=None):
        pass

    @abstractmethod
    def on_show_file_property(self, event=None):
        pass

    @abstractmethod
    def handle_back_effect(self, event=None):
        pass

    @abstractmethod
    def handle_next_effect(self, event=None):
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
    def icons_path(self) -> Path:
        """
        アイコンフォルダのパスを取得します。
        :return: アイコンフォルダのパス
        """
        raise NotImplementedError()

    @property
    def font_sizes(self) -> FontSize:
        """
        フォントサイズを取得します。
        :return: フォントサイズ
        """
        raise NotImplementedError()

    @property
    def theme_colors(self) -> ThemeColors:
        """
        テーマ色を取得します。
        :return: テーマ色フォントサイズ
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

    @property
    def file_property_visible(self):
        """
        画像ファイルのプロパティウィンドウの表示・非表示状態
        :return: true:表示, false: 非表示
        """
        raise NotImplementedError()

    @file_property_visible.setter
    def file_property_visible(self, visible: bool):
        """
        ファイルプロパティウィンドウの表示・非表示状態を設定します。
        :param visible: true:表示, false: 非表示
        """
        raise NotImplementedError()

    @property
    def current_effect(self) -> MosaicEffect:
        """
        選択中のエフェクトを取得します。
        :return: 選択中のエフェクト
        """
        raise NotImplementedError()

    @abstractmethod
    def update_data_state(self, state: DATA_STATE):
        pass
