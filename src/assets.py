# -*- coding: utf-8 -*-
"""
    Assets
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


@dataclass(frozen=True)
class Assets:
    """
    Assetを管理
    """
    def __init__(self, config_file: Path):
        """
        コンストラクタ
        :param config_file: 設定ファイルのパス
        """
        self.config_file = config_file
        self.settings = self.load_config()

    def load_config(self) -> dict:
        """
        JSONファイルから設定を読み込むメソッド。
        :return: 読み込んだ設定を含む辞書
        """
        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            # ファイルが存在しない場合のデフォルト設定
            config = {
                "font_sizes": {
                    "h1": 24,
                    "h2": 20,
                    "h3": 18,
                    "h4": 16,
                    "h5": 14,
                    "body": 16  # 本文のデフォルトフォントサイズ
                }
            }
            return config


