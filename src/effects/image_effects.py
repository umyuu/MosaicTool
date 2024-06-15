"""
image_effects モジュール

画像にエフェクトを適用するためのクラスを提供します。
現在はモザイクエフェクトをサポートしています。
"""
from collections import OrderedDict
from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Optional, Any

from PIL import Image

from .. utils import round_up_decimal


@dataclass(frozen=True)
class MosaicEffect:
    """
    画像にモザイクエフェクトを適用する機能を提供します。
    """
    cell_size: int  # モザイクのセルサイズを指定します
    MIN_CELL_SIZE: Final[int] = 4  # 最小セルサイズ
    AUTO: Final[int] = -1  # 自動計算の定数

    @property
    def name(self) -> str:
        """
        エフェクト名
        """
        if self.cell_size == MosaicEffect.AUTO:
            return "mosaic_auto"

        return f"mosaic_{self.cell_size}"

    def apply(self, image: Image.Image, start_x: int, start_y: int, end_x: int, end_y: int) -> bool:
        """
        画像の指定された領域にモザイクを適用する
        :param image: モザイクをかける画像
        :param start_x: モザイクをかける領域の左上X座標
        :param start_y: モザイクをかける領域の左上Y座標
        :param end_x: モザイクをかける領域の右下X座標
        :param end_y: モザイクをかける領域の右下Y座標
        :return: モザイクをかけたかどうか
        """
        # モザイクをかける領域のサイズを計算
        region_width = end_x - start_x
        region_height = end_y - start_y

        # 領域の幅または高さが0以下の場合、モザイク処理をスキップする
        if region_width <= 0 or region_height <= 0:
            return False

        # セルサイズが最小セルサイズ未満の場合、エラーを発生させる
        if self.cell_size < MosaicEffect.MIN_CELL_SIZE:
            raise ValueError(f"MosaicEffect cell_size:{self.cell_size}")

        # 指定された領域にモザイク効果を適用
        region = self.apply_mosaic_to_region(image, start_x, start_y, end_x, end_y, region_width, region_height)

        # モザイクをかけた領域を元の画像に戻す
        image.paste(region, (start_x, start_y, start_x + region.width, start_y + region.height))
        return True

    def apply_mosaic_to_region(self, image: Image.Image, start_x: int, start_y: int, end_x: int, end_y: int, region_width: int, region_height: int) -> Image.Image:
        """
        指定された領域にモザイク効果を適用する
        :param image: モザイクをかける画像
        :param start_x: 領域の左上X座標
        :param start_y: 領域の左上Y座標
        :param end_x: 領域の右下X座標
        :param end_y: 領域の右下Y座標
        :param region_width: 領域の幅
        :param region_height: 領域の高さ
        :return: モザイク効果が適用された領域画像
        """
        # 画像から指定された領域を切り出す
        region = image.crop((start_x, start_y, end_x, end_y))

        # セルサイズに基づいて縮小後のサイズを計算
        new_width = (region_width // self.cell_size) * self.cell_size
        new_height = (region_height // self.cell_size) * self.cell_size

        # 領域をセルサイズに揃えてリサイズするための四角形のサイズを計算
        region = region.resize((new_width // self.cell_size, new_height // self.cell_size), Image.Resampling.BOX)
        region = region.resize((new_width, new_height), Image.Resampling.NEAREST)

        return region

    @staticmethod
    def calc_cell_size(image: Image.Image) -> int:
        """
        画像のサイズに基づいてモザイクのセルサイズを計算します。

        :param image: セルサイズを計算する対象の画像
        :return: 計算されたセルサイズ
        """
        # 長辺を100で割って小数点以下を切り上げます。
        # セルサイズが最小4ピクセル未満の場合は、4ピクセルに設定します。
        long_side: Decimal = Decimal(max(image.width, image.height))
        cell_size = max(MosaicEffect.MIN_CELL_SIZE, round_up_decimal(long_side / Decimal(100), 0))
        return int(cell_size)


class EffectPreset:
    """
    エフェクトのプリセットを管理する機能を提供します。
    """
    def __init__(self, presets: dict[str, Any] = {}):
        """
        コンストラクタ
        :param presets: プリセットの設定情報
        """
        self.presets: OrderedDict[str, MosaicEffect] = OrderedDict({})

        mosaics = presets.get("mosaic", {})
        for key in mosaics.get("cell_sizes", []):
            mosaic = MosaicEffect(key)
            self.add_preset(mosaic.name, mosaic)

        # デフォルト値を選択します。
        default_effect = MosaicEffect(mosaics.get("default", {}).get("cell_size", 0))   
        retval = self.presets.get(default_effect.name, None)
        if retval is not None:  # 設定値が存在する時
            self._default_preset = default_effect.name
            return

        keys = list(self.presets.keys())
        val = keys[len(keys) // 2 - 1]

        self._default_preset = val

    @property
    def default_preset(self) -> str:
        """
        デフォルトのプリセット名を取得します。
        :return: プリセット名
        """
        return self._default_preset

    def add_preset(self, name: str, effect: MosaicEffect):
        """
        プリセットを追加します
        :param name: プリセットの名前
        :param effect: プリセットのエフェクトオブジェクト
        """
        self.presets[name] = effect

    def get_preset(self, name: str) -> MosaicEffect:
        """
        プリセットを取得します
        :param name: プリセットの名前
        :return: プリセットのエフェクトオブジェクト
        """
        return self.presets.get(name, MosaicEffect(0))

    def back_preset(self, current_name: str) -> tuple[str, MosaicEffect]:
        """
        指定したキーの前のキーと値を取得する。
        前のキーが存在しない場合、一番最後のキーと値を返す。
        :param current_name: 現在の名前
        :return: 前のキーとその値。前のキーが存在しない場合は一番最後のキーと値を返す。
        """
        keys = list(self.presets.keys())
        try:
            # 現在のキーのインデックスを取得
            current_index = keys.index(current_name)
            # 前のインデックスを計算
            back_index = (current_index - 1) % len(keys)
            back_key = keys[back_index]
            return back_key, self.presets[back_key]
        except ValueError:
            # 現在のキーが存在しない場合
            return "", MosaicEffect(0)

    def next_preset(self, current_name: str) -> tuple[str, MosaicEffect]:
        """
        指定したキーの次のキーと値を取得する。
        次のキーが存在しない場合、一番先頭のキーと値を返す。
        :param current_name: 現在の名前
        :return: 次のキーとその値。次のキーが存在しない場合は一番先頭のキーと値を返す。
        """
        keys = list(self.presets.keys())
        try:
            # 現在のキーのインデックスを取得
            current_index = keys.index(current_name)
            # 次のインデックスを計算
            next_index = (current_index + 1) % len(keys)
            next_key = keys[next_index]
            return next_key, self.presets[next_key]
        except ValueError:
            return "", MosaicEffect(0)
