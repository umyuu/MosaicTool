# -*- coding: utf-8 -*-
"""
    models
    データモデル関連
"""

from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
from typing import Any, Optional, Literal, Callable

from . app_config import AppConfig
from . effects.image_effects import MosaicEffect

# 画像形式
ImageFormat = {
    'PNG': ('*.png', ),
    'JPEG': ('*.jpg', '*.jpeg', ),
    'WEBP': ('*.webp', ),
    'BMP': ('*.bmp', ),
    'PNM': ('*.pbm', '*.pgm', '*.ppm', )
}


@dataclass(frozen=True)
class ImageFileInfo:
    """
    画像ファイル情報
    """
    width: int = 0  # 幅
    height: int = 0  # 高さ
    file_path: Path = Path()  # ファイルパス
    CURRENT_DIR: Path = Path()  # ファイルパス

    @property
    def mtime(self) -> str:
        """
        最終更新日時をISO 8601形式で取得する
        :return: 最終更新日時の文字列
        """
        if ImageFileInfo.CURRENT_DIR == self.file_path:
            return ""
        # ファイルのメタデータを取得
        file_stat = self.file_path.stat()
        # 最終更新日時を取得
        timestamp = file_stat.st_mtime
        # タイムスタンプをローカルタイムに変換し、ISO 8601形式に変換
        local_time = datetime.fromtimestamp(timestamp)
        return local_time.strftime('%Y-%m-%dT%H:%M:%S')

    @property
    def file_size(self) -> int:
        """
        ファイルサイズを取得する
        :return: ファイルサイズ（バイト）
        """
        if ImageFileInfo.CURRENT_DIR == self.file_path:
            return 0
        return os.path.getsize(self.file_path)


@dataclass(frozen=True)
class StatusBarInfo(ImageFileInfo):
    """
    ステータスバーのステータスメッセージ
    """
    current: int = 0  # 現在のindex
    total: int = 0  # トータル


# 画像データの状態
DATA_STATE = Literal["Modified", "Unchanged"]


class AppDataModel:
    """
    アプリのデータモデル
    """
    def __init__(self, settings: AppConfig):
        """
        初期化処理
        :param settings: アプリの設定情報
        """
        self._settings = settings
        self.image_list: list[Path] = []
        self.current: int = 0
        # 許可される拡張子のリスト
        self.allowed_extensions = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg"]
        self.file_property_visible: bool = False
        # ディレクトリをドロップ時
        self._is_save_directory: bool = False
        self._data_state: DATA_STATE = "Unchanged"
        # モザイク加工後の画像を保存するイベントハンドラー
        self.data_saved_handler: Callable
        # プリセット
        self._current_preset_name = settings.effect_presets.default_preset
        self._current_effect = settings.effect_presets.get_preset(self._current_preset_name)

    def add_images(self, image_list: list[Path]) -> int:
        """
        画像ファイルを追加します。
        :param image_list: 画像ファイルのリスト
        :return: 追加した件数
        """
        count: int = 0
        for image in image_list:
            if not self.check_image_file(image):
                continue
            self.image_list.append(image)
            count += 1
        return count

    def get(self, key: str, default=None) -> Any:
        """
        設定値を取得する。
        :param key: 取得する設定ファイルのキー
        :param default: キーが存在しない場合に返されるデフォルト値
        :return: 設定値
        """
        return self.settings.get(key, default)

    @property
    def data_state(self) -> DATA_STATE:
        """
        画像データの状態を取得します。
        :return: データの状態
        """
        return self._data_state

    @data_state.setter
    def data_state(self, value: DATA_STATE):
        """
        画像データの状態を設定します。
        :param value: 設定する状態
        """
        self._data_state = value

    @property
    def save_directory(self) -> bool:
        """
        モザイクファイルの保存先
        :return: ディレクトリに保存時は、true。同一フォルダに保存時は、false
        """
        return self._is_save_directory

    @save_directory.setter
    def save_directory(self, value: bool):
        """
        モザイクファイルの保存先
        :param value: ディレクトリに保存時は、true。同一フォルダに保存時は、false
        """
        self._is_save_directory = value

    @property
    def settings(self) -> AppConfig:
        """
        設定情報を取得する。
        :return: 設定情報
        """
        return self._settings

    @property
    def count(self) -> int:
        """
        処理対象の総件数
        :return: 総件数
        """
        return len(self.image_list)

    def check_image_file(self, file_path: Path) -> bool:
        """
        画像ファイルの検証
        ファイルの存在、許可された拡張子かをチェックします。
        :param file_path: チェックするファイルパス
        :return: チェック結果 正常:true、検証エラー:false
        """
        if not file_path.exists():
            return False
        return self.is_allowed_extension(file_path)

    def is_allowed_extension(self, file_path: Path) -> bool:
        """
        ファイルの拡張子が許可されているかどうかをチェックする関数
        大文字小文字を無視してチェックします。
        :param file_path: チェックするファイルのパス
        :return: 拡張子が許可されている場合はTrue、そうでない場合はFalse
        """
        return file_path.suffix.lower() in self.allowed_extensions  

    def clear(self):
        """
        モデルをクリアします。
        モザイク加工中の画像があれば保存イベントを呼び出します。
        """
        self.commit()
        self.image_list = []
        self.current = 0
        self._is_save_directory = False

    def commit(self):
        """
        編集内容を確定し、ファイルを保存します。
        """
        if self.data_saved_handler:  # データ保存イベントが登録時
            if self.data_state == "Unchanged":
                return
            self.data_saved_handler(None)

    def back_image(self):
        """
        インデックスを前の画像に移動します。
        """
        self.commit()
        if self.current > 0:
            self.current -= 1
        #else:
        #    raise IndexError("Already at the first file in the list.")

    def next_image(self):
        """
        インデックスを次の画像に移動します。
        """
        self.commit()
        if self.current < len(self.image_list) - 1:
            self.current += 1
        #else:
        #    raise IndexError("No more files in the list.")

    def get_current_image(self) -> Optional[Path]:
        """
        現在処理中の画像
        :return: ファイルパス
        """
        if self.image_list:
            return self.image_list[self.current]
        return None

    @property
    def current_effect(self) -> MosaicEffect:
        """
        選択中のエフェクトを返します。
        :return: 選択中のエフェクト
        """
        return self._current_effect

    def back_effect(self):
        """
        前のエフェクトに切り替えます。
        """
        preset_name, effect = self.settings.effect_presets.back_preset(self._current_preset_name)
        if len(preset_name) == 0:
            raise ValueError("back_effect")

        self._current_preset_name = preset_name
        self._current_effect = effect

    def next_effect(self):
        """
        次のエフェクトに切り替えます。
        """
        preset_name, effect = self.settings.effect_presets.next_preset(self._current_preset_name)
        if len(preset_name) == 0:
            raise ValueError("next_effect")

        self._current_preset_name = preset_name
        self._current_effect = effect

    def __str__(self) -> str:
        """
        print用の文字列。デバック用に使用します。
        :return: モデルの情報
        """
        return f"current:{self.current}, {self.image_list}"
