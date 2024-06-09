# -*- coding: utf-8 -*-
"""
    models
    データモデル関連
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from functools import lru_cache

import os
from pathlib import Path
from typing import List, Any
import time

from PIL import Image
from PIL.PngImagePlugin import PngInfo

from . utils import round_up_decimal


# 画像形式
ImageFormat = {
    'PNG': ('*.png', ),
    'JPEG': ('*.jpg', '*.jpeg', ),
    'WEBP': ('*.webp', ),
    'BMP': ('*.bmp', ),
    'PNM': ('*.pbm', '*.pgm', '*.ppm', )
}


@dataclass
class StatusMessage:
    """
    ステータスバーのステータスメッセージ
    """
    width: int = 0
    height: int = 0
    current: int = 0
    total: int = 0
    file_size: int = 0  # ファイルサイズ(バイト単位)
    mtime: str = ""


class DataModel:
    """
    処理対象のファイル
    """
    def __init__(self):
        self.file_paths: List[Path] = []
        self.current: int = 0

    def add_file_path(self, file_path: Path) -> int:
        """
        処理対象のファイルを追加します。
        :return: 追加件数
        """
        if file_path.exists():
            self.file_paths.append(file_path)
            return 1
        return 0

    def count(self) -> int:
        return len(self.file_paths)

    def clear(self):
        self.file_paths = []
        self.current = 0

    def set_current(self, current: int):
        if current < 0 or current >= len(self.file_paths):
            raise ValueError(f"current index out of range: {current}")
        self.current = current

    def next_index(self):
        """
        current の次のインデックスに移動します。
        """
        if self.current < len(self.file_paths) - 1:
            self.current += 1
        #else:
        #    raise IndexError("No more files in the list.")

    def prev_index(self):
        """
        current の前のインデックスに移動します。
        """
        if self.current > 0:
            self.current -= 1
        #else:
        #    raise IndexError("Already at the first file in the list.")

    def get_file_paths(self) -> List[Path]:
        """
        処理対象のファイル一覧
        """
        return self.file_paths

    def get_current_file(self) -> Path:
        """
        現在処理中のファイルパス
        """
        return self.file_paths[self.current]

    def __str__(self) -> str:
        return f"current:{self.current}, {self.file_paths}"


@dataclass
class MosaicImageFile:
    """
    モザイク画像ファイルの情報を管理するクラス
    """
    file_path: Path

    @classmethod
    def is_png(cls, path: Path):
        # ファイルの存在を確認する
        if not path.is_file():
            return False

        # ファイルをバイナリモードで開く
        with open(path, 'rb') as f:
            # 先頭8バイトを読み取る
            header = f.read(8)

        # ファイルが8バイト未満の場合はPNGファイルではないと見なす
        if len(header) < 8:
            return False

        # PNGのシグネチャが存在するかどうかを確認する
        return header[:8] == b'\x89PNG\r\n\x1a\n'

    @classmethod
    def is_jpg(cls, path: Path):
        # ファイルの存在を確認する
        if not path.is_file():
            return False

        # ファイルをバイナリモードで開く
        with open(path, 'rb') as f:
            # 先頭2バイトを読み取る
            header = f.read(2)

        # ファイルが2バイト未満の場合はJPGファイルではないと見なす
        if len(header) < 2:
            return False

        # 先頭バイトがJPGファイルのマジックナンバーであるかどうかを確認する
        return header == b'\xFF\xD8'

    @property
    def mtime(self) -> str:
        """
        最終更新日時をISO 8601形式で取得するプロパティ
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
    def st_size(self) -> int:
        """
        ファイルサイズを取得するプロパティ
        :return: ファイルサイズ（バイト）
        """
        return os.path.getsize(self.file_path)

    @classmethod
    def get_image_size(cls, file_path: Path) -> tuple[int, int]:
        """
        画像の大きさを取得します。
        :return: width, height
        """
        with Image.open(file_path) as img:
            return img.size

    @classmethod
    def get_image_info(cls, file_path: Path) -> dict[Any, Any]:
        """
        画像のInfoを取得します。
        :return: info
        """
        with Image.open(file_path) as img:
            return img.info

    @classmethod
    def newFileName(cls, file_path: Path) -> Path:
        """
        モザイク処理後の新しいファイル名を生成する
        同名ファイルが存在する場合は、画像の大きさを比較します。
        :return: 新しいファイルのPathオブジェクト
        """
        size = (0, 0)

        try:
            size = MosaicImageFile.get_image_size(file_path)
        except Exception as e:
            print(e)

        # 元のファイル名から新しいファイル名を作成
        for i in range(0, 1000):
            newFileName = file_path.with_stem(file_path.stem + f"_mosaic_{i}")
            if not newFileName.exists():
                return newFileName
            try:
                new_size = MosaicImageFile.get_image_size(newFileName)
                if size == new_size:
                    return newFileName  # 画像の大きさが同じなら
                if size == (0, 0):
                    return newFileName  # 元ファイルが削除されている場合
            except Exception as e:
                print(e)
                time.sleep(3)

        if i == 1000:
            ValueError()
        return newFileName


@dataclass
class MosaicFilter:
    """
    モザイク画像を作成するクラス
    """
    _image: Image.Image
    cell_size: int = field(init=False)  # モザイクのセルサイズ

    def __post_init__(self):
        """
        モザイクのセルサイズを計算し設定します。
        """
        self.cell_size = self.calc_cell_size()

    def save(self, output_path: Path, filename: Path):
        """
        モザイク画像を保存する
        :param output_path: 保存するファイルの名前
        """
        if MosaicImageFile.is_png(filename):
            with Image.open(filename) as img:
                self.save_png_metadata(img, self._image, output_path)
            return
        if MosaicImageFile.is_jpg(filename):
            with Image.open(filename) as img:
                self.save_jpeg_metadata(img, self._image, output_path)
            return

        self._image.save(output_path)

    def save_png_metadata(self, src_image: Image.Image, out_image: Image.Image, output_path: Path):
        """
        PNGの場合の処理
        """
        png_info = src_image.info
        new_png_info = PngInfo()
        for key, value in png_info.items():
            new_png_info.add_text(key, value)
        out_image.save(output_path, pnginfo=new_png_info)
        print("PNGINFO saved successfully.")

    def save_jpeg_metadata(self, image: Image.Image, out_image: Image.Image, output_path: Path):
        """
        JPEGの場合
        """
        exif_data = image.info.get("exif")
        if exif_data:
            out_image.save(output_path, exif=exif_data)
        else:
            out_image.save(output_path)

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
        long_side = (Decimal(self._image.width).max(Decimal(self._image.height))) / Decimal(100)
        cell_size = max(4, round_up_decimal(long_side, 0))  # 最小4ピクセル
        return int(cell_size)