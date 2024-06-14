# -*- coding: utf-8 -*-
"""
    Widgets Core
    画面パーツのコア部分
"""
import tkinter as tk
from typing import Optional, Literal


class WidgetUtils(object):
    """
    ウィジェット用のユーティリティ
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
    ウィジェットにツールチップを表示する
    """
    def __init__(self, widget, text: str):
        """
        コンストラクタ
        :param widget (tk.Widget): ツールチップを表示する対象のウィジェット
        :param text: ツールチップに表示するテキスト
        """
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.handle_enter)
        self.widget.bind("<Leave>", self.handle_leave)

    def handle_enter(self, event=None):
        """
        マウスがウィジェットに入ったときに発生します。
        :param event: イベント
        """
        self.id = self.widget.after(500, self.on_show_tooltip)  # 500ミリ秒後にshow_tooltipメソッドを呼び出す

    def handle_leave(self, event=None):
        """
        マウスがウィジェットから離れたときに発生します。
        :param event: イベント
        """
        if hasattr(self, 'id'):
            self.widget.after_cancel(self.id)  # 予定されていたツールチップ表示をキャンセルする
            if self.tooltip:
                self.tooltip.destroy()  # ツールチップが表示されていればそれを破棄する

    def on_show_tooltip(self, event=None):
        """
        ツールチップを表示する
        :param event: イベント
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
    def __init__(self, master=None, image_path: str = "", tooltip_text: Optional[str] = None, **kwargs):
        """
        コンストラクタ
        :param master: 親ウィジェット
        :param image_path: ボタンに表示する画像のファイルパス
        :param tooltip_text: ツールチップに表示するテキスト
        :param kwargs: その他のオプション
        """
        photo_image = tk.PhotoImage(file=image_path)
        photo_image = photo_image.subsample(3, 3)
        super().__init__(master, image=photo_image, compound="top", **kwargs)

        self.photo_image = photo_image  # ガベージコレクションを防ぐために画像を保持
        self.tooltip = Tooltip(self, tooltip_text) if tooltip_text else None


class LabelTextEntry(tk.Frame):
    """
    ラベルとテキストのカスタムコンポーネント
    """
    def __init__(self, master=None, **kwargs):
        """
        コンストラクタ
        :param master: 親ウィジェット
        :param kwargs: その他のオプション
        """
        super().__init__(master)

        #_, font_size = font
        self.label = tk.Label(self, **kwargs)
        self.label.pack(side=tk.LEFT)

        self.text_entry = tk.Entry(self, **kwargs)
        self.text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def get_text(self) -> str:
        """
        テキストエントリの内容を取得するメソッド。
        :return: テキストエントリの内容。
        """
        return self.text_entry.get()

    def set_label_background_color(self, bg: str):
        """
        ラベルの背景色を設定します。
        :param bg: 設定する背景色
        """
        self.label.config(bg=bg)

    def set_text_background_color(self, bg: str):
        """
        テキストの背景色を設定します。
        :param bg: 設定する背景色
        """
        self.text_entry.config(bg=bg)

    def set_text(self, text: str):
        """
        テキストエントリに指定されたテキストを設定するメソッド。
        :param label_text: 設定するテキスト
        """
        self.text_entry.delete(0, tk.END)  # 既存のテキストを削除
        self.text_entry.insert(0, text)


class RightClickMenu(tk.Menu):
    """
    右クリックメニュー
    """
    def __init__(self, root):
        """
        コンストラクタ
        :param root: 親ウィジェット
        """
        super().__init__(root, tearoff=0)
        self.add_command(label="カット", command=self.handle_cut)
        self.add_command(label="コピー", command=self.handle_copy)
        self.add_command(label="ペースト", command=self.handle_paste)
        self.widget = None

    def on_show_menu(self, event):
        """
        右クリックメニューを表示します
        """
        self.widget = event.widget
        self.tk_popup(event.x_root, event.y_root)

    def handle_cut(self):
        """
        切り取りボタンをクリック時に発生します。
        """
        if self.widget:
            self.widget.event_generate("<<Cut>>")

    def handle_copy(self):
        """
        コピーボタンをクリック時に発生します。
        """
        if self.widget:
            self.widget.event_generate("<<Copy>>")

    def handle_paste(self):
        """
        貼り付けボタンをクリック時に発生します。
        """
        if self.widget:
            self.widget.event_generate("<<Paste>>")
