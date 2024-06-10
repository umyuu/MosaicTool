# -*- coding: utf-8 -*-
"""
ImageFileService
このモジュールは、画像ファイルの読み込み、保存、処理など、画像ファイルに関連する操作を扱う ImageFileService クラスを提供します。
"""
from pathlib import Path
import time
from typing import Any

from PIL import Image
from PIL.PngImagePlugin import PngInfo
#from .models import MosaicImageFile


class ImageFileService:
    """
    画像ファイルに関連する操作を提供するクラスです。

    Attributes:
        None
    """
    @staticmethod
    def is_png(path: Path) -> bool:
        """
        渡されたファイルがPNG形式かどうかを判定します。

        Args:
            path (Path): ファイルのパス

        Returns:
            bool: PNG形式かどうかの真偽値
        """
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

    @staticmethod
    def is_jpg(path: Path) -> bool:
        """
        渡されたファイルがJPEG形式かどうかを判定します。

        Args:
            path (Path): ファイルのパス

        Returns:
            bool: JPEG形式かどうかの真偽値
        """
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

    @staticmethod
    def load(file_path: Path) -> Image.Image:
        # 日本語ファイル名でエラーが発生するため。openを使用する。
        """
        """
        return Image.open(file_path)

    @staticmethod
    def get_image_size(file_path: Path) -> tuple[int, int]:
        """
        画像の大きさを取得します。

        Args:
            file_path (Path): 画像ファイルのパス

        Returns:
            tuple[int, int]: 画像の幅と高さのタプル
        """
        with Image.open(file_path) as img:
            return img.size

    @staticmethod
    def get_image_info(file_path: Path) -> dict[Any, Any]:
        """
        画像の情報を取得します。

        Args:
            file_path (Path): 画像ファイルのパス

        Returns:
            dict[Any, Any]: 画像の情報を格納した辞書
        """
        with Image.open(file_path) as img:
            return img.info

    @staticmethod
    def save(_image: Image.Image, output_path: Path, filename: Path):
        """
        画像保存処理
        """
        # Todo: PNGINFOの情報はテストパターンを増やす。
        # ファイルの読み込み処理を改善する。
        # DataModel側に保持する。
        if ImageFileService.is_png(filename):
            with Image.open(filename) as img:
                ImageFileService.save_png_metadata(img, _image, output_path)
            return
        if ImageFileService.is_jpg(filename):
            with Image.open(filename) as img:
                ImageFileService.save_jpeg_metadata(img, _image, output_path)
            return

        _image.save(output_path)

    @staticmethod
    def save_png_metadata(src_image: Image.Image, out_image: Image.Image, output_path: Path) -> None:
        """
        PNG形式の画像にメタデータを保存します。

        Args:
            src_image (Image.Image): 元画像
            out_image (Image.Image): 出力画像
            output_path (Path): 出力先ファイルパス

        Returns:
            None
        """
        png_info = src_image.info
        if png_info:
            new_png_info = PngInfo()
            for key, value in png_info.items():
                # 値がint型であれば、文字列に変換してから追加する
                if isinstance(value, int):
                    value = str(value)
                # 値がfloat型であれば、文字列に変換してから追加する
                elif isinstance(value, float):
                    value = str(value)
                # 値がtuple型であれば、文字列に変換してから追加する
                elif isinstance(value, tuple):
                    value = ', '.join(map(str, value))

                new_png_info.add_itxt(key, value)

            out_image.save(output_path, pnginfo=new_png_info)
            print("PNGINFO saved successfully.")
        else:
            out_image.save(output_path)

    @staticmethod
    def save_jpeg_metadata(image: Image.Image, out_image: Image.Image, output_path: Path) -> None:
        """
        JPEG形式の画像にメタデータを保存します。

        Args:
            image (Image.Image): 元画像
            out_image (Image.Image): 出力画像
            output_path (Path): 出力先ファイルパス

        Returns:
            None
        """
        exif_data = image.info.get("exif")
        if exif_data:
            out_image.save(output_path, exif=exif_data)
        else:
            out_image.save(output_path)

    @staticmethod
    def mosaic_filename(file_path: Path) -> Path:
        """
        モザイク処理後の新しいファイル名を生成します。
        同名ファイルが存在する場合は、画像の大きさを比較します。

        Args:
            file_path (Path): 元画像ファイルのパス

        Returns:
            Path: 新しいファイル名のパス
        """
        size = (0, 0)

        try:
            size = ImageFileService.get_image_size(file_path)
        except Exception as e:
            print(e)

        # 元のファイル名から新しいファイル名を作成
        for i in range(0, 1000):  # rangeは1から1000まで動作します
            newFileName = file_path.with_stem(file_path.stem + f"_mosaic_{i}")
            if not newFileName.exists():
                return newFileName  # ファイルが存在しなければ新しいファイル名を返す
            try:
                new_size = ImageFileService.get_image_size(newFileName)
                if size == new_size:
                    return newFileName  # 画像の大きさが同じなら新しいファイル名を返す
                if size == (0, 0):
                    return newFileName  # 元ファイルが削除されている場合は新しいファイル名を返す
            except Exception as e:
                print(e)
                time.sleep(3)

        if i == 1000:
            raise ValueError("Failed to generate a new file name after 1000 attempts.")
        return newFileName
