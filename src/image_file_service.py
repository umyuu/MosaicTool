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

        :param path: ファイルのパス
        :return: PNG形式かどうかの真偽値
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
        :param path: ファイルのパス
        :return: JPEG形式かどうかの真偽値
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
        """
        画像ファイルを読み込みます。
        :param file_path: 画像ファイルのパス
        :return: 画像データ
        """
        #print("load" + str(file_path))
        return Image.open(file_path)

    @staticmethod
    async def load_async(file_path: Path) -> Image.Image:
        """
        画像ファイルを非同期で読み込みます。
        :param file_path: 画像ファイルのパス
        :return: 画像データ
        """
        print("load_async" + str(file_path))
        return Image.open(file_path)

    @staticmethod
    def get_image_size(file_path: Path) -> tuple[int, int]:
        """
        画像の大きさを取得します。
        :param file_path: 画像ファイルのパス
        :return: 画像の幅と高さ
        """
        with Image.open(file_path) as img:
            return img.size

    @staticmethod
    def get_image_info(file_path: Path) -> dict[Any, Any]:
        """
        画像の情報を取得します。
        :param file_path: 画像ファイルのパス
        :return: 画像の情報を格納した辞書
        """
        with Image.open(file_path) as img:
            return img.info

    @staticmethod
    def save(out_image: Image.Image, output_path: Path, filename: Path):
        """
        画像保存処理
        :param out_image: 出力画像
        :param output_path: 出力先ファイルパス
        :param filename: 元画像のファイルパス
        """
        # Todo: PNGINFOの情報はテストパターンを増やす。
        # 元ファイルを読み込み部分を廃止する。
        # DataModel側に保持する。
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True)

        if ImageFileService.is_png(filename):
            with Image.open(filename) as src_img:
                ImageFileService.save_png_metadata(src_img, out_image, output_path)
            return
        if ImageFileService.is_jpg(filename):
            with Image.open(filename) as src_img:
                ImageFileService.save_jpeg_metadata(src_img, out_image, output_path)
            return
        out_image.save(output_path)

    @staticmethod
    async def save_async(mode, size: tuple[int, int], data: bytes, output_path: Path, filename: Path):
        """
        画像保存処理(非同期)
        Image.Imageはpickle化を行えないため、bytes型で渡します。
        :param mode: カラーモード
        :param size: 出力画像サイズ
        :param data: 出力画像
        :param output_path: 出力先ファイルパス
        :param filename: 元画像のファイルパス
        """
        out_image = Image.frombytes(mode, size, data)
        ImageFileService.save(out_image, output_path, filename)

    @staticmethod
    def save_png_metadata(src_image: Image.Image, out_image: Image.Image, output_path: Path) -> None:
        """
        PNG形式の画像にメタデータを保存します。
        :param src_image: 元画像
        :param out_image: 出力画像
        :param output_path: 出力先ファイルパス
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
        else:
            out_image.save(output_path)

    @staticmethod
    def save_jpeg_metadata(src_image: Image.Image, out_image: Image.Image, output_path: Path) -> None:
        """
        JPEG形式の画像にメタデータを保存します。
        :param src_image: 元画像
        :param out_image: 出力画像
        :param output_path: 出力先ファイルパス
        """
        exif_data = src_image.info.get("exif")
        if exif_data:
            out_image.save(output_path, exif=exif_data)
        else:
            out_image.save(output_path)

    @staticmethod
    def mosaic_filename(file_path: Path, is_dir: bool = False) -> Path:
        """
        モザイク適用済みのファイルパスを生成します。
        同名ファイルが存在する場合は、画像の大きさを比較します。
        :param file_path: 元画像のファイルのパス
        :param is_dir: ディレクトリの場合はTrue
        :return: モザイク適用済みのファイルパス
        """
        size = (0, 0)

        try:
            size = ImageFileService.get_image_size(file_path)
        except Exception as e:
            print(e)

        new_file = file_path
        if is_dir:  # 新しいディレクトリパスを作成
            # パスの親ディレクトリとファイル名を取得
            parent_dir = file_path.parent
            file_name = file_path.name

            # ディレクトリ名の末尾に_mosaicを付ける
            new_parent_dir = parent_dir.with_name(parent_dir.name + '_mosaic')
            new_file = new_parent_dir / file_name
        return ImageFileService.generate_new_filename(new_file, size)

    @staticmethod
    def generate_new_filename(base_path: Path, size: tuple[int, int]) -> Path:
        """
        新しいファイル名を生成します。同名ファイルが存在する場合は、画像の大きさを比較します。
        :param base_path: 元となるファイルパス
        :param size: 元画像のサイズ
        :return: 新しいファイルパス
        """
        # 元のファイル名から新しいファイル名を作成
        for i in range(0, 1000):  # rangeは1から1000まで動作します
            new_filename = base_path.with_stem(base_path.stem + f"_mosaic_{i}")
            if not new_filename.exists():
                return new_filename  # ファイルが存在しなければ新しいファイル名を返します。
            try:
                new_size = ImageFileService.get_image_size(new_filename)
                if size == new_size:
                    return new_filename  # 画像の大きさが同じなら新しいファイル名を返します。
                if size == (0, 0):
                    return new_filename  # 元ファイルが削除されている場合、新しいファイル名を返します。
            except Exception as e:
                print(e)
                time.sleep(3)

        if i == 1000:
            raise ValueError("Failed to generate a new file name after 1000 attempts.")
        return new_filename
