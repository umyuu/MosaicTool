# -*- coding: utf-8 -*-
"""
    AppController
"""
from pathlib import Path
from typing import Callable, Iterable, Optional
import re

from . app_config import AppConfig, FontSize, ThemeColors
from . models import AppDataModel, StatusBarInfo, DATA_STATE
from . image_file_service import ImageFileService
from . utils import Stopwatch
from . abstract_controllers import AbstractAppController
from . widgets import MainPage
from . effects.image_effects import MosaicEffect


class AppController(AbstractAppController):
    """
    アプリのコントローラー
    """
    def __init__(self, model: AppDataModel, view: MainPage, window_title_callback: Callable):
        """
        コンストラクタ
        """
        self.model = model
        self.view = view
        self.window_title_callback = window_title_callback
        # ドラッグ＆ドロップで渡されたパスを分割する正規表現
        self.drop_file_split = re.compile(r'([A-Za-z]:[/|\\\\].*?(?=[A-Za-z]:[/|\\\\]|$))', re.RegexFlag.UNICODE)
        self.image_controller = ImageController(self)
        # 自動保存イベントを登録します。
        self.model.data_saved_handler = self.handle_auto_save
        # アイコンフォルダ
        self._icons_path: Path

    def add_file_path(self, file_path: Path) -> int:
        """
        ファイルをデータモデルに追加します。
        パスがディレクトリの場合は、ディレクトリ内のファイルも追加します。
        :param file_path: 画像ファイルのパス
        :return: 追加件数
        """
        if not file_path.is_dir():  # ファイルの場合
            return self.model.add_images([file_path])

        files: list[Path] = []
        for f in file_path.glob("*.*"):  # ディレクトリの場合
            files.append(f)
        if len(files) != 0:
            self.model.save_directory = True
        return self.model.add_images(files)

    def get_current_image(self) -> Optional[Path]:
        """
        現在選択されている画像のパス
        """
        return self.model.get_current_image()

    def handle_drop(self, event):
        """
        ドロップ完了時に発生する。
        :param event: ドロップイベント
        """
        sw = Stopwatch.start_new()

        count: int = 0
        event_data = event.data  # ドラッグ&ドロップで渡されたファイル名
        if not event_data:
            self.view.set_status_message("No data received in drop event")
            self.display_process_time(f"{sw.elapsed:.3f}s")
            return

        print(event_data)
        self.model.clear()
        for match in re.finditer(self.drop_file_split, event_data):
            group = match.group()
            if not group:
                continue

            # 日本語が含まれるパスの場合{C:\画像パス}となるため除外する。
            f = group.rstrip(" {").rstrip("} ")
            path = Path(f)
            count += self.add_file_path(path)

        if count > 0:
            self.update_view(sw)

        self.view.set_status_message(f"received in drop files:{count}")
        self.display_process_time(f"{sw.elapsed:.3f}s")

    @property
    def current_effect(self) -> MosaicEffect:
        return self.model.current_effect

    def on_file_open(self, event=None):
        """
        ファイル選択ボタンクリック時
        :param event: イベント
        """
        self.view.on_file_open(None)

    def handle_auto_save(self, event=None):
        """
        画像ファイルの自動保存
        :param event: イベント
        """
        current = self.model.get_current_image()
        if current is None:
            return
        if self.model.data_state == "Unchanged":
            return  # アプリの閉じるボタンより
        mosaic_filename = ImageFileService.mosaic_filename(current, self.model.save_directory)
        self.view.on_save(mosaic_filename, False)

    def on_save_as(self, event=None):
        """
        ファイルを選択して保存ボタンをクリック時
        :param event: イベント
        """
        current = self.model.get_current_image()
        if current is None:
            return
        mosaic_filename = ImageFileService.mosaic_filename(current, self.model.save_directory)
        self.view.on_save_as(None, mosaic_filename)

    def handle_back_image(self, event=None):
        """
        前の画像に遷移するをクリック時
        :param event: イベント
        """
        sw = Stopwatch.start_new()
        self.model.back_image()
        self.update_view(sw)

    def handle_next_image(self, event=None):
        """
        次の画像に遷移するをクリック時
        :param event: イベント
        """
        sw = Stopwatch.start_new()
        self.model.next_image()
        self.update_view(sw)

    def on_show_file_property(self, event=None):
        """
        画像情報を表示するをクリック時
        :param event: イベント
        """
        if self.model.count == 0:
            return
        status = self.get_status()
        image_info = ImageFileService.get_image_info(status.file_path)
        self.view.on_show_file_property(status, str(image_info))

    @property
    def file_property_visible(self):
        """
        画像ファイルのプロパティウィンドウの表示・非表示状態
        :return: true:表示, false: 非表示
        """
        return self.model.file_property_visible

    @file_property_visible.setter
    def file_property_visible(self, visible: bool):
        """
        ファイルプロパティウィンドウの表示・非表示状態を設定します。
        :param visible: true:表示, false: 非表示
        """
        self.model.file_property_visible = visible

    @property
    def icons_path(self) -> Path:
        """
        アイコン画像のフォルダパス
        :return: フォルタパス
        """
        return self._icons_path

    @icons_path.setter
    def icons_path(self, path: Path):
        """
        アイコンフォルダのパスを設定します。
        :param path: アイコンフォルダのパス
        """
        self._icons_path = path

    def handle_back_effect(self, event=None):
        """
        前のエフェクトに切り替えます。
        :param event: イベント
        """
        self.model.back_effect()
        self.view.update_header_view(event)

    def handle_next_effect(self, event=None):
        """
        次のエフェクトに切り替えます。
        :param event: イベント
        """
        self.model.next_effect()
        self.view.update_header_view(event)

    def update_view(self, sw: Optional[Stopwatch] = None):
        """
        Viewを更新します。
        画面に画像と処理時間を表示します。
        :param sw: ストップウォッチ
        """
        current_image = self.model.get_current_image()
        if current_image is not None:
            self.view.display_image(current_image)

        is_visible: bool = self.model.file_property_visible
        if is_visible:  # ファイルのプロパティウィンドウが表示中
            self.on_show_file_property(None)

        # 処理時間を表示します。
        if sw:
            self.display_process_time(f"{sw.elapsed:.3f}s")

    def update_data_state(self, state: DATA_STATE):
        """
        画像のデータの状態を変更します。
        :param state: データの状態
        """
        self.model.data_state = state

    def update_status_bar_file_info(self):
        """
        ステータスバーのファイル情報部分を更新します。
        """
        self.view.on_update_status_bar(self.get_status())

    def handle_select_files_complete(self, files: Iterable[str]):
        """
        ファイル選択ダイアログよりファイル選択時
        :param files: ファイル一覧
        """
        sw = Stopwatch.start_new()
        count: int = 0  # カウントは画像件数
        total: int = 0  # ファイル選択ダイアログより選択した件数(画像ファイル以外も含みます)

        self.model.clear()
        for file_path in files:
            count += self.add_file_path(Path(file_path))
            total += 1
        if count == 0:
            self.view.set_status_message("No image file selected")
            return

        self.update_view(sw)
        self.view.set_status_message(f"Select files:{count} / {total}")

    @property
    def font_sizes(self) -> FontSize:
        return self.model.settings.font_sizes

    @property
    def theme_colors(self) -> ThemeColors:
        return self.model.settings.theme_colors

    def get_mosaic_filename(self) -> Path:
        """
        モザイク適用後のファイル名を生成します。
        :return: Path
        """
        f = self.model.get_current_image()
        if f is not None:
            return ImageFileService.mosaic_filename(f, self.model.save_directory)
        raise ValueError("get_mosaic_filename")

    def set_window_title(self, text: Path):
        """
        タイトルバーの設定
        :param text: ファイルパス
        """
        self.window_title_callback(text)

    def display_process_time(self, time: str) -> None:
        """
        処理時間の設定
        :param time: 処理時間
        """
        self.view.on_update_process_time(time)

    def get_status(self) -> StatusBarInfo:
        """
        ステータスメッセージを取得します。
        """
        total = self.model.count
        if total == 0:
            return StatusBarInfo()

        file_path = self.model.get_current_image()
        if file_path is None:
            return StatusBarInfo()

        width, height = ImageFileService.get_image_size(file_path)

        return StatusBarInfo(
            current=self.model.current + 1,
            total=total,
            file_path=file_path,
            width=width,
            height=height
        )

    def get_view(self):
        return self.view

    def get_config(self) -> AppConfig:
        return self.model.settings


class ImageController:
    def __init__(self, app_controller: AppController):
        self.app_controller = app_controller

    def update_view(self):
        pass
        #current_image = self.model.get_current_image()
        #view = self.app_controller.get_view()
        #        view.display_image(current_image)

    def next_image(self):
        #       self.model.next_image()
        #view = self.app_controller.get_view()
        self.update_view()

    def previous_image(self):
        #        self.model.previous_image()
        self.update_view()

    def apply_mosaic(self):
        pass
        #coordinates = self.view.get_mosaic_coordinates()
        #modified_image = self.model.apply_mosaic(coordinates)
        # self.view.display_image(modified_image)
