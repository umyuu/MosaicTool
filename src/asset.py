# -*- coding: utf-8 -*-
"""
    Asset
"""
from pathlib import Path
from typing import Literal, Optional

from PIL import Image, ImageTk

IMAGE_NAMES = Literal["file_open", "save_as", "arrow_back", "arrow_forward", "info",
                      "content_copy", "settings"]


class Asset:
    """
    Assetを管理するクラス
    """
    def __init__(self, image_paths: dict[str, Path]):
        """
        コンストラクタ
        :param image_paths: 読み込む画像ファイルのパスを含む辞書
        """
        self.image_paths = image_paths
        self.images: dict[str, Image.Image] = {}
        self.tk_images: dict[str, ImageTk.PhotoImage] = {}

    def load_image(self, name: str, path: Path):
        """
        画像を読み込む
        :param name: 画像の名前（辞書のキーとして使用）
        :param path: 画像ファイルのパス
        """
        image = Image.open(path)
        self.images[name] = image

    def load_all_images(self):
        """
        全ての画像を読み込む
        """
        [self.load_image(name, path) for name, path in self.image_paths.items()]

    def get_image(self, name: IMAGE_NAMES) -> Image.Image:
        """
        読み込んだPillowのImageオブジェクトを取得する
        :param name: 画像の名前
        :return: PillowのImageオブジェクト
        """
        return self.images[name]

    def get_tk_image(self, name: IMAGE_NAMES):
        """
        読み込んだTkinter用のImageオブジェクトを取得する
        :param name: 画像の名前
        :return: Tkinter用のImageオブジェクト
        """
        tk_image = self.tk_images.get(name)
        if tk_image is not None:
            return tk_image

        image = self.images[name]
        # 画像をサブサンプリングする（3倍縮小）
        pil_image = image.resize((image.width // 3, image.height // 3), Image.Resampling.BICUBIC)
        # PillowのImageTkモジュールを使用して、ImageオブジェクトをTkinterのPhotoImageに変換する
        self.tk_images[name] = ImageTk.PhotoImage(pil_image)

        return self.tk_images[name]
