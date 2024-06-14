# -*- coding: utf-8 -*-
"""
    models
    データモデル関連
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
import os
from pathlib import Path
from typing import Any, List

from PIL import Image

from . utils import round_up_decimal
from . app_config import AppConfig

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
    file_path: Path = Path("")  # ファイルパス
    #file_size: int = 0  # ファイルサイズ(バイト単位)
    #mtime: str = ""  # モザイクを掛ける対象ファイルの最終更新日時

    @property
    def mtime(self) -> str:
        """
        最終更新日時をISO 8601形式で取得する
        :return: 最終更新日時の文字列
        """
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
        return os.path.getsize(self.file_path)


@dataclass(frozen=True)
class StatusBarInfo(ImageFileInfo):
    """
    ステータスバーのステータスメッセージ
    """
    current: int = 0  # 現在のindex
    total: int = 0  # トータル


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
        self.image_list: List[Path] = []
        self.current: int = 0
        # 許可される拡張子のリスト
        self.allowed_extensions = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg"]
        self.file_property_visible: bool = False

    def add_images(self, image_list: List[Path]) -> int:
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
        設定を取得する。
        :param key: 取得する設定のキー
        :param default: キーが存在しない場合に返されるデフォルト値
        :return: 設定の値
        """
        return self.settings.get(key, default)

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
        :param file_path: チェックするファイルのパス
        :return: 拡張子が許可されている場合はTrue、そうでない場合はFalse
        """
        # 大文字小文字を無視してチェックする
        return file_path.suffix.lower() in self.allowed_extensions  

    def clear(self):
        """
        モデルをクリアします。
        """
        self.image_list = []
        self.current = 0

    def next_image(self):
        """
        インデックスを次の画像に移動します。
        """
        if self.current < len(self.image_list) - 1:
            self.current += 1
        #else:
        #    raise IndexError("No more files in the list.")

    def previous_image(self):
        """
        インデックスを前の画像に移動します。
        """
        if self.current > 0:
            self.current -= 1
        #else:
        #    raise IndexError("Already at the first file in the list.")

    def get_current_image(self) -> Path:
        """
        現在処理中の画像
        :return: ファイルパス
        """
        if self.image_list:
            return self.image_list[self.current]
        return Path("")

    def __str__(self) -> str:
        """
        print用の文字列。デバック用に使用します。
        :return: モデルの情報
        """
        return f"current:{self.current}, {self.image_list}"


@dataclass
class MosaicFilter:
    """
    モザイク画像を作成するクラス
    """
    _image: Image.Image
    cell_size: int = field(init=False)  # モザイクのセルサイズ
    min_cell_size: int = 4  # 最小セルサイズ

    def __post_init__(self):
        """
        モザイクのセルサイズを計算し設定します。
        """
        self.cell_size = self.calc_cell_size()

    def apply(self, start_x: int, start_y: int, end_x: int, end_y: int) -> bool:
        """
        指定された領域にモザイクを適用する
        :param start_x: モザイクをかける領域の左上X座標
        :param start_y: モザイクをかける領域の左上Y座標
        :param end_x: モザイクをかける領域の右下X座標
        :param end_y: モザイクをかける領域の右下Y座標
        :return: モザイクを掛けてたかどうか
        """
        # モザイクをかける領域のサイズを計算
        region_width = end_x - start_x
        region_height = end_y - start_y

        # 領域の幅と高さの値がどちらかが0の場合、モザイク処理をSkipします。
        if (region_width == 0) or (region_height == 0):
            return False

        # モザイクをかける領域を切り出す
        region = self._image.crop((start_x, start_y, end_x, end_y))

        # セルサイズに基づいて縮小後のサイズを計算
        new_width = (region_width // self.cell_size) * self.cell_size
        new_height = (region_height // self.cell_size) * self.cell_size

        # 領域をセルサイズに揃えてリサイズするための四角形のサイズを計算
        region = region.resize((new_width // self.cell_size, new_height // self.cell_size), Image.Resampling.BOX)
        region = region.resize((new_width, new_height), Image.Resampling.NEAREST)

        # モザイクをかけた領域を元の画像に戻す
        self._image.paste(region, (start_x, start_y, start_x + new_width, start_y + new_height))
        return True

    @property
    def Image(self) -> Image.Image:
        """
        モザイク処理後の画像データを取得する。
        :return: 画像データ
        """
        return self._image

    def calc_cell_size(self) -> int:
        """
        モザイクのセルサイズを計算します。

        :return: セルサイズ
        """
        # 長辺の取得し÷100で割り、小数点以下を切り上げする。
        # セルサイズが4以下（を含む）場合は、最小4ピクセルに設定します。
        long_side = (Decimal(self._image.width).max(Decimal(self._image.height))) / Decimal(100)
        cell_size = max(self.min_cell_size, round_up_decimal(long_side, 0))  # 最小4ピクセル
        return int(cell_size)
