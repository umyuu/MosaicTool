# -*- coding: utf-8 -*-
"""
    AppConfig
"""
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Literal


@dataclass(frozen=True)
class FontSize:
    h1: int
    h2: int
    h3: int
    h4: int
    h5: int
    body: int


class AppConfig:
    """
    アプリケーションの構成
    """
    def __init__(self, config_file: Path):
        """
        コンストラクタ
        :param config_file: 設定ファイルのパス
        """
        self.config_file = config_file
        self.settings = self.load_config()

        font_sizes = self.settings['font_sizes']
        self._font_sizes = FontSize(h1=int(font_sizes.get("h1")),
                                    h2=int(font_sizes.get("h2")),
                                    h3=int(font_sizes.get("h3")),
                                    h4=int(font_sizes.get("h4")),
                                    h5=int(font_sizes.get("h5")),
                                    body=int(font_sizes.get("body")))

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
                "themes": {
                    "primary_hue": "#44F7D3",
                    "secondary_hue": "#2ecc71",
                    "neutral_hue": "#95a5a6",
                },
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

    def save_config(self):
        """
        設定をJSONファイルに保存するメソッド。
        """
        with open(self.config_file, "w", encoding="utf-8") as file:
            json.dump(self.settings, file, ensure_ascii=False, indent=4)

    def get(self, key: str, default=None) -> Any:
        """
        設定を取得するメソッド。
        :param key: 取得する設定のキー
        :param default: キーが存在しない場合に返されるデフォルト値
        :return: 設定の値
        """
        return self.settings.get(key, default)

    @property
    def primary_hue(self) -> str:
        """
        プライマリ色
        :return: 色
        """
        return self.settings['themes'].get("primary_hue")

    @property
    def secondary_hue(self) -> str:
        """
        セカンダリ色
        :return: 色
        """
        return self.settings['themes'].get("secondary_hue")

    @property
    def neutral_hue(self) -> str:
        """
        ニュートラル色
        :return: 色
        """
        return self.settings['themes'].get("neutral_hue")

    @property
    def font_sizes(self) -> FontSize:
        """
        フォントサイズ
        :return: フォントサイズ
        """
        return self._font_sizes

    def get_font_size(self, element: Literal["h1", "h2", "h3", "h4", "h5", "body"]) -> int:
        """
        指定した要素（見出しや本文）の文字サイズを取得するメソッドです。
        :param element: 見出しの種類（'h1', 'h2', 'h3', 'h4', 'h5'）または 'body'（本文）
        :return: フォントサイズ
        """
        return self.settings['font_sizes'].get(element, 16)  # デフォルト値は16

    def set(self, key: str, value):
        """
        設定を更新するメソッド。
        :param key: 更新する設定のキー
        :param key: 更新する値
        """
        self.settings[key] = value
        self.save_config()

    def __str__(self) -> str:
        return str(self.settings)
