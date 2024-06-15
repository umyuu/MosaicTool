"""
image_effects モジュール

画像にエフェクトを適用するためのクラスを提供します。
現在はモザイクエフェクトをサポートしています。
"""
from typing import Dict

from PIL import Image


class MosaicEffect:
    """
    画像にモザイクエフェクトを適用する機能を提供します。
    """
    def __init__(self, cell_size: int):
        """
        コンストラクタ
        :param cell_size: モザイクのセルサイズを指定します
        """
        self.cell_size = cell_size

    def apply(self, image: Image.Image, start_x: int, start_y: int, end_x: int, end_y: int) -> bool:
        """
        画像の指定された領域にモザイクを適用する
        :param image: モザイクをかける画像
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
        region = image.crop((start_x, start_y, end_x, end_y))

        # セルサイズに基づいて縮小後のサイズを計算
        new_width = (region_width // self.cell_size) * self.cell_size
        new_height = (region_height // self.cell_size) * self.cell_size

        # 領域をセルサイズに揃えてリサイズするための四角形のサイズを計算
        region = region.resize((new_width // self.cell_size, new_height // self.cell_size), Image.Resampling.BOX)
        region = region.resize((new_width, new_height), Image.Resampling.NEAREST)

        # モザイクをかけた領域を元の画像に戻す
        image.paste(region, (start_x, start_y, start_x + new_width, start_y + new_height))
        return True


class EffectPreset:
    """
    エフェクトのプリセットを管理する機能を提供します。
    """
    def __init__(self):
        """
        コンストラクタ
        エフェクトプリセットを管理するための辞書を初期化します
        """
        self.presets: Dict[str, MosaicEffect] = {}

    def add_preset(self, name: str, effect: MosaicEffect):
        """
        プリセットを追加します
        :param name: プリセットの名前
        :param effect: プリセットのエフェクトオブジェクト
        """
        self.presets[name] = effect

    def get_preset(self, name: str):
        """
        プリセットを取得します
        :param name: プリセットの名前
        :return: プリセットのエフェクトオブジェクト（存在しない場合はNone）
        """
        return self.presets.get(name)
