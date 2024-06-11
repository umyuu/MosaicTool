from dataclasses import dataclass
import sys
import os
import unittest
from pathlib import Path
import tkinter
import tkinterdnd2
# プロジェクトのルートディレクトリをシステムパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import Stopwatch
import app


class TestAppController(unittest.TestCase):
    """コントローラーをテストするクラス"""
    def test_drop_file(self):
        """
        ドラッグ＆ドロップのテスト
        """
        current_dir = Path(__file__).parent
        assets = [
            str(current_dir / "test_files/jet_256x256.webp"),
            str(current_dir / "test_files/test_image_png_pnginfo_valid.png"),
            # 日本語ファイル名の場合
            "{" + str(current_dir / "test_files/test_image_png_pnginfo_valid.png") + "}",
        ]

        @dataclass
        class Event:
            data: str

        my_app = app.MyApp()
        my_app.after_launch([])

        event = Event(' '.join(assets))

        controller = my_app.controller
        controller.handle_drop(event)
        count = controller.model.count()

        self.assertTrue(count == 3, f"test_drop_file_parser error {count}")


if __name__ == "__main__":
    unittest.main()
