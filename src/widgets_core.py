# -*- coding: utf-8 -*-
"""
    Widgets Core
    画面パーツのコア部分
"""
import tkinter as tk
from typing import Optional, Literal


class WidgetUtils(object):
    """
    ウィジェット用のユーティリティクラス
    """
    @staticmethod
    def bind_all(widget: tk.Widget,
                 modifier: Literal["Control", "Shift", "Alt", "Control-Shift", ""] = "",
                 letter: str = "",
                 callback=None) -> None:
        """
        キーボードショートカットを割り当てるメソッド。
        :param widget: ショートカットを割り当てる対象のウィジェット
        :param modifier: キー修飾子 ("Control", "Shift", "Alt" など)
        :param letter: ショートカットキーとして使用する文字
        :param callback: イベント発生時に呼び出されるコールバック関数
        :return: None
        """
        if not callback:
            raise ValueError("コールバック関数を指定する必要があります")

        bind_modifier = f"{modifier}-" if modifier else ""

        # 大文字と小文字の両方にバインド
        # キーが矢印キーかどうかをチェック
        if letter in ["Left", "Right", "Up", "Down"]:
            widget.bind_all(f"<{bind_modifier}{letter}>", callback)
        else:
            # 大文字と小文字の両方にバインド
            widget.bind_all(f"<{bind_modifier}{letter.upper()}>", callback)
            if not letter.isdecimal():
                widget.bind_all(f"<{bind_modifier}{letter.lower()}>", callback)


class Tooltip:
    """
    ウィジェットにツールチップを表示するクラス
    """
    def __init__(self, widget, text: str):
        """
        初期化メソッド

        Parameters:
        widget (tk.Widget): ツールチップを表示する対象のウィジェット
        text (str): ツールチップに表示するテキスト
        """
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.enter)  # マウスがウィジェットに入ったときにenterメソッドを呼び出す
        self.widget.bind("<Leave>", self.leave)  # マウスがウィジェットから離れたときにleaveメソッドを呼び出す

    def enter(self, event=None):
        """
        マウスがウィジェットに入ったときに呼び出されるメソッド
        """
        self.id = self.widget.after(500, self.show_tooltip)  # 500ミリ秒後にshow_tooltipメソッドを呼び出す

    def leave(self, event=None):
        """
        マウスがウィジェットから離れたときに呼び出されるメソッド
        """
        if hasattr(self, 'id'):
            self.widget.after_cancel(self.id)  # 予定されていたツールチップ表示をキャンセルする
            if self.tooltip:
                self.tooltip.destroy()  # ツールチップが表示されていればそれを破棄する

    def show_tooltip(self, event=None):
        """
        ツールチップを表示するメソッド
        """
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 32
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", border=1, padx=8, pady=4)
        label.pack(ipadx=1)


class PhotoImageButton(tk.Button):
    """
    画像ボタンのクラス
    """
    def __init__(self, master=None, image_path: str = "", tooltip_text: Optional[str] = None, command=None, **kwargs):
        """
        コンストラクタ
        :param master: 親ウィジェット
        :param image_path: ボタンに表示する画像のファイルパス
        :param tooltip_text: ツールチップに表示するテキスト
        :param command: ボタンが押されたときに実行するコマンド
        :param kwargs: その他のオプション
        """
        img = tk.PhotoImage(file=image_path)
        img = img.subsample(3, 3)
        if command is None:
            super().__init__(master, image=img, compound="top", **kwargs)
        else:
            super().__init__(master, image=img, compound="top", command=command, **kwargs)

        self.img = img  # ガベージコレクションを防ぐために画像を保持
        self.tooltip = Tooltip(self, tooltip_text) if tooltip_text else None
