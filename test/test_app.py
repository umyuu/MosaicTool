import sys
import os

# プロジェクトのルートディレクトリをシステムパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from src.utils import Stopwatch
from app import MyApp


class TestAppLaunchTime(unittest.TestCase):
    """アプリの起動時間をテストするクラス"""
    def test_app_starts_within_3_seconds(self):
        """
        3秒未満でアプリが起動する。
        """
        sw = Stopwatch.start_new()

        test_app = MyApp()
        test_app.after_launch([])  # ここでアプリの起動をシミュレート
        elapsed = sw.elapsed

        self.assertTrue(elapsed < 3, f"App launch time was {elapsed} seconds, which is longer than the threshold.")


if __name__ == "__main__":
    unittest.main()
