# -*- coding: utf-8 -*-
"""
    models
    データモデル関連
"""
from dataclasses import dataclass
from decimal import Decimal
import time
import os
from pathlib import Path

from PIL import Image

from . utils import round_up_decimal


@dataclass
class MosaicImageFile:
    """
    モザイク画像ファイルの情報を管理するクラス
    """
    _file_path: str = ""
    # ファイルのメタデータを取得
    file_stat = Path(_file_path).stat()

    @property
    def mtime(self) -> str:
        """
        最終更新日時をISO 8601形式で取得するプロパティ
        :return: 最終更新日時の文字列
        """
        # 最終更新日時を取得
        timestamp = self.file_stat.st_mtime
        # タイムスタンプをISO 8601形式に変換
        return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(timestamp))

    @property
    def st_size(self) -> int:
        """
        ファイルサイズを取得するプロパティ
        :return: ファイルサイズ（バイト）
        """
        return os.path.getsize(self._file_path)

    def newMosaicFile(self) -> Path:
        """
        モザイク処理後の新しいファイル名を生成する
        :return: 新しいファイルのPathオブジェクト
        """
        mosaic = Path(self._file_path)
        # 元のファイル名から新しいファイル名を作成
        return mosaic.with_stem(mosaic.stem + "_mosaic")


@dataclass
class MosaicImage:
    """
    モザイク画像を作成するクラス
    """
    _image: Image.Image
    cell_size: int = 10  # モザイクのセルサイズを固定値に設定

    def save(self, filename: str):
        """
        モザイク画像を保存する
        :param filename: 保存するファイルの名前
        """
        self._image.save(filename)

    def apply(self, start_x: int, start_y: int, end_x: int, end_y: int):
        """
        指定された領域にモザイクを適用する
        :param start_x: モザイクをかける領域の左上X座標
        :param start_y: モザイクをかける領域の左上Y座標
        :param end_x: モザイクをかける領域の右下X座標
        :param end_y: モザイクをかける領域の右下Y座標
        """
        # モザイクをかける領域のサイズを計算
        region_width = end_x - start_x
        region_height = end_y - start_y

        # モザイクをかける領域を切り出す
        region = self._image.crop((start_x, start_y, end_x, end_y))

        # セルサイズに基づいて縮小後のサイズを計算
        new_width = max(1, region_width // self.cell_size)
        new_height = max(1, region_height // self.cell_size)

        # 縮小してから元のサイズにリサイズ
        region = region.resize((new_width, new_height), Image.BOX).resize(region.size, Image.NEAREST)
        # モザイクをかけた領域を元の画像に戻す
        self._image.paste(region, (start_x, start_y, end_x, end_y))

    @property
    def Image(self) -> Image.Image:
        """
        モザイク処理された画像を取得するプロパティ
        :return: PIL Imageオブジェクト
        """
        return self._image

    def calc_cell_size(self) -> int:
        """
        モザイクのセルサイズを計算します。

        :return: セルサイズ
        """
        # 長辺の取得し÷100で割り、小数点以下を切り上げする。
        # セルサイズが4以下（を含む）場合は、最小4ピクセルに設定します。
        long_side = Decimal(self._image.width).max(Decimal(self._image.height)) / Decimal(100)
        cell_size = max(4, round_up_decimal(Decimal(long_side), 0))  # 最小4ピクセル
        return int(cell_size)
