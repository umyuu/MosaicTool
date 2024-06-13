# -*- coding: utf-8 -*-
"""
    AppConfig
"""
from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ThemeColors:
    """
    テーマ色
    """
    primary: str = "#44F7D3"  # プライマリ色
    secondary: str = "#CCCCCC"  # セカンダリ色
    neutral: str = "SystemWindow"  # ニュートラル色
    info: str = "RosyBrown"  # アクセント色
    text: str = "ivory"  # テキストの色


@dataclass(frozen=True)
class FontSize:
    """
    フォントサイズ
    """
    h1: int = 24  # 見出し1
    h2: int = 20  # 見出し2
    h3: int = 18  # 見出し3
    h4: int = 16  # 見出し4
    h5: int = 14  # 見出し5
    body: int = 16  # 本文


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
            primary=theme_colors.get("primary"),
            secondary=theme_colors.get("secondary"),
            neutral=theme_colors.get("neutral"),
            info=theme_colors.get("info"),
            text=theme_colors.get("text"),
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
                "version": 1,
                "initialWindowSize": {
                    "width": 800,
                    "height": 600,
                },
                "filePropertyWindowSize": {
                    "width": 600,
                    "height": 500,
                },
                "theme_colors": asdict(ThemeColors()),
                "font_sizes": asdict(FontSize()),
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
