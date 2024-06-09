# -*- coding: utf-8 -*-
"""ユーティリティ"""
from decimal import Decimal, ROUND_UP


def get_package_version() -> str:
    """
    バージョン情報を取得します。
    """
    return '0.0.2'


def round_up_decimal(value: Decimal, places: int) -> Decimal:
    """
    指定した小数点以下の桁数に切り上げる関数

    :param value: 対象のDecimal値
    :param places: 小数点以下の桁数
    :return: 切り上げられたDecimal値
    """
    # '0.'の後に'0'を places 個並べて Decimal オブジェクトを作成
    quantize_str = '0.' + '0' * places
    # 指定した桁数に切り上げる
    rounded_value = value.quantize(Decimal(quantize_str), rounding=ROUND_UP)
    return rounded_value
