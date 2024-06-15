"""
appの単体テスト
"""
import sys
import os
import unittest

# プロジェクトのルートディレクトリをシステムパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import Stopwatch
from app import MyApp


class TestAppLaunchTime(unittest.TestCase):
    """アプリの起動時間をテストするクラス"""
    def setUp(self):
        """テストのセットアップを行います。"""
        self.current_dir = os.path.dirname(__file__)

    @unittest.skipIf(os.name != 'nt', "Skipping The OS is not Windows")
    def test_app_starts_within_3_seconds(self):
        """
        アプリの起動時間が3秒未満
        """
        image_path = os.path.join(self.current_dir, 'test_files', 'jet_256x256.webp')

        sw = Stopwatch.start_new()

        test_app = MyApp()
        test_app.after_launch([image_path])  # ここでアプリの起動をシミュレート

        elapsed = sw.elapsed
        print(f"{elapsed:.3f}", end=None)
        self.assertTrue(elapsed < 3, f"App launch time was {elapsed:.3f} seconds, which is longer than the threshold.")


if __name__ == "__main__":
    unittest.main()
