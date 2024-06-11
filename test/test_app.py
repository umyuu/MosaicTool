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
        3秒未満でアプリが起動。
        """
        current_dir = os.path.dirname(__file__)
        image_path = os.path.join(current_dir, 'test_files', 'jet_256x256.webp')

        sw = Stopwatch.start_new()

        test_app = MyApp()
        test_app.after_launch([image_path])  # ここでアプリの起動をシミュレート

        elapsed = sw.elapsed
        print(f"{elapsed:.3f}", end=None)
        self.assertTrue(elapsed < 3, f"App launch time was {elapsed:.3f} seconds, which is longer than the threshold.")


if __name__ == "__main__":
    unittest.main()
