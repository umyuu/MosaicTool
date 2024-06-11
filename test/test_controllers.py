from dataclasses import dataclass
import sys
import os
import unittest
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
        @dataclass
        class Event:
            data: str

        current_dir = os.path.dirname(__file__)
        my_app = app.MyApp()
        my_app.after_launch([])
        event = Event("")
        controller = my_app.controller
        controller.handle_drop(event)

        count = controller.model.count()
        print(f"count:{count}", end=None)
#        self.assertTrue(elapsed < 3, f"App launch time was {elapsed:.3f} seconds, which is longer than the threshold.")


if __name__ == "__main__":
    unittest.main()
