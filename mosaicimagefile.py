# -*- coding: utf-8 -*-
"""
    MosaicImageFile
"""
from dataclasses import dataclass
from pathlib import Path
import time

from PIL import Image


@dataclass
class MosaicImageFile:
    _file_path: str = ""
    # ファイルのメタデータを取得
    file_stat = Path(_file_path).stat()

    @property
    def mtime(self) -> str:
        # 最終更新日時を取得
        timestamp = self.file_stat.st_mtime
        # タイムスタンプをISO 8601形式に変換
        return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(timestamp))

    @property
    def st_size(self) -> int:
        return self.file_stat.st_size

    def saveMosaic(self) -> Path:
        mosaic = Path(self._file_path)
        # 元のファイル名から新しいファイル名を作成
        return mosaic.with_stem(mosaic.stem + "_mosaic")


class MosaicImage:
    def __init__(self, image: Image.Image):
        self.image = image

    def save(self, filename: str):
        self.image.save(filename)

    def apply_mosaic(self, start_x: int, start_y: int, end_x: int, end_y: int):
        # モザイクをかける領域を切り出す
        region = self.image.crop((start_x, start_y, end_x, end_y))
        # 切り出した領域を縮小し、元のサイズに拡大することでモザイクをかける
        region = region.resize((10, 10), Image.BOX).resize(region.size, Image.NEAREST)
        #モザイクをかけた領域を元の画像に戻す
        self.image.paste(region, (start_x, start_y, end_x, end_y))

    def get_image(self):
        return self.image
