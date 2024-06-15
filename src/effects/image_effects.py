"""
image_effects モジュール

画像にエフェクトを適用するためのクラスを提供します。
現在はモザイクエフェクトをサポートしています。
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict

from PIL import Image

from .. utils import round_up_decimal


@dataclass(frozen=True)
class MosaicEffect:
    """
    画像にモザイクエフェクトを適用する機能を提供します。
    """
    cell_size: int  # モザイクのセルサイズを指定します
    _MIN_CELL_SIZE: int = 4  # 最小セルサイズ

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

    @staticmethod
    def calc_cell_size(image: Image.Image) -> int:
        """
        画像のサイズに基づいてモザイクのセルサイズを計算します。

        :param image: セルサイズを計算する対象の画像
        :return: 計算されたセルサイズ
        """
        # 長辺を100で割って小数点以下を切り上げます。
        # セルサイズが最小4ピクセル未満の場合は、4ピクセルに設定します。
        long_side = (Decimal(image.width).max(Decimal(image.height))) / Decimal(100)
        cell_size = max(MosaicEffect._MIN_CELL_SIZE, round_up_decimal(long_side, 0))
        return int(cell_size)


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