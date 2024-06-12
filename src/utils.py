# -*- coding: utf-8 -*-
"""ユーティリティ"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_UP
import time


def get_package_version() -> str:
    """
    バージョン情報を取得します。
    """
    return '0.0.4'


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


@dataclass
class Stopwatch:
    """
    経過時間を計測するためのクラス。
    Example:
        from src.utils import Stopwatch

        watch = Stopwatch.start_new()
        ### 計測する処理
        print(f"{watch.elapsed:.3f}")
    """
    _start_time: float = 0
    _elapsed: float = 0
    _is_running: bool = False

    @property
    def elapsed(self) -> float:
        """
        計測中の経過時間を取得します。

        Returns:
            float: 計測中の経過時間(小数秒)
        """
        if self._is_running:
            self._elapsed = time.perf_counter() - self._start_time

        return self._elapsed

    @property
    def is_running(self) -> bool:
        """
        計測が実行中であるかどうかを取得します
        """
        return self._is_running

    def start(self) -> None:
        """
        計測を開始します。
        """
        self._start_time = time.perf_counter()
        self._elapsed = 0
        self._is_running = True

    @classmethod
    def start_new(cls) -> 'Stopwatch':
        """
        新しいストップウォッチを生成し、計測を開始します。

        Returns:
            Stopwatch: 新しいストップウォッチオブジェクト
        """
        stopwatch = Stopwatch()
        stopwatch.start()
        return stopwatch

    def stop(self) -> float:
        """
        計測を終了し、経過時間を返します。

        Returns:
            float: 計測中の経過時間
        """
        if self._is_running:
            self._elapsed = time.perf_counter() - self._start_time
            self._is_running = False
        return self._elapsed
