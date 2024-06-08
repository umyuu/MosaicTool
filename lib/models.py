# -*- coding: utf-8 -*-
"""
    models
    データモデル関連
"""
from dataclasses import dataclass
from pathlib import Path
import time

from PIL import Image


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
        return self.file_stat.st_size

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
        # モザイクをかける領域を切り出す
        region = self._image.crop((start_x, start_y, end_x, end_y))
        # 切り出した領域を縮小し、元のサイズに拡大することでモザイクをかける
        region = region.resize((10, 10), Image.BOX).resize(region.size, Image.NEAREST)
        # モザイクをかけた領域を元の画像に戻す
        self._image.paste(region, (start_x, start_y, end_x, end_y))

    @property
    def Image(self) -> Image.Image:
        """
        モザイク処理された画像を取得するプロパティ
        :return: PIL Imageオブジェクト
        """
        return self._image
