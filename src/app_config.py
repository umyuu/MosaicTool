# -*- coding: utf-8 -*-
"""
    AppConfig
"""
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FontSize:
    """
    フォントサイズ
    """
    h1: int  # 見出し1
    h2: int  # 見出し2
    h3: int  # 見出し3
    h4: int  # 見出し4
    h5: int  # 見出し5
    body: int  # 本文


@dataclass(frozen=True)
class ThemeColors:
    """
    テーマ色
    """
    primary_hue: str  # プライマリ色
    secondary_hue: str  # セカンダリ色
    neutral_hue: str  # ニュートラル色
    accent: str  # アクセント色


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

        theme_colors = self.settings['theme_colors']
        self._theme_colors = ThemeColors(
            primary_hue=theme_colors.get("primary_hue"),
            secondary_hue=theme_colors.get("secondary_hue"),
            neutral_hue=theme_colors.get("neutral_hue"),
            accent=theme_colors.get("accent"),
        )

        font_sizes = self.settings['font_sizes']
        self._font_sizes = FontSize(
            h1=int(font_sizes.get("h1")),
            h2=int(font_sizes.get("h2")),
            h3=int(font_sizes.get("h3")),
            h4=int(font_sizes.get("h4")),
            h5=int(font_sizes.get("h5")),
            body=int(font_sizes.get("body")),
        )

    def load_config(self) -> dict:
        """
        JSONファイルから設定を読み込む。
        :return: 読み込んだ設定を含む辞書
        """
        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            # ファイルが存在しない場合のデフォルト設定
            config = {
                "theme_colors": {
                    "primary_hue": "#44F7D3",
                    "secondary_hue": "#2ECC71",
                    "neutral_hue": "#95A5A6",
                    "accent": "#FF0000",
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
        設定をJSONファイルに保存する。
        """
        with open(self.config_file, "w", encoding="utf-8") as file:
            json.dump(self.settings, file, ensure_ascii=False, indent=4)

    def get(self, key: str, default=None) -> Any:
        """
        設定を取得する。
        :param key: 取得する設定のキー
        :param default: キーが存在しない場合に返されるデフォルト値
        :return: 設定の値
        """
        return self.settings.get(key, default)

    @property
    def theme_colors(self) -> ThemeColors:
        """
        テーマ色
        :return: テーマ色
        """
        return self._theme_colors

    @property
    def font_sizes(self) -> FontSize:
        """
        フォントサイズ
        :return: フォントサイズ
        """
        return self._font_sizes

    def set(self, key: str, value):
        """
        設定を更新する。
        :param key: 更新する設定のキー
        :param key: 更新する値
        """
        self.settings[key] = value
        self.save_config()

    def __str__(self) -> str:
        """
        ToString
        :return: 設定情報の文字列
        """
        return str(self.settings)
