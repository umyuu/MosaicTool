"""
appの単体テスト
"""
import os
from pathlib import Path
import sys
import unittest

# プロジェクトのルートディレクトリをシステムパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.asset import Asset
from src.utils import Stopwatch

from app import MyApp


class TestAppLaunch(unittest.TestCase):
    """アプリの起動をテストするクラス"""
    def setUp(self):
        """テストのセットアップを行います。"""
        self.current_dir = os.path.dirname(__file__)
        self.image_path = Path(self.current_dir, 'test_files', 'jet_256x256.webp')

    def test_app_asset_load(self):
        """
        アイコン画像の読み込みテスト
        """
        icons_path = Path(self.current_dir, "..", "third_party/icons")
        asset = Asset({
            "file_open": icons_path / "file_open_24dp_FILL0_wght400_GRAD0_opsz24.png",
            "save_as": icons_path / "save_as_24dp_FILL0_wght400_GRAD0_opsz24.png",
            "arrow_back": icons_path / "arrow_back_24dp_FILL0_wght400_GRAD0_opsz24.png",
            "arrow_forward": icons_path / "arrow_forward_24dp_FILL0_wght400_GRAD0_opsz24.png",
            "info": icons_path / "info_24dp_FILL0_wght400_GRAD0_opsz24.png",
            "content_copy": icons_path / "content_copy_24dp_FILL0_wght400_GRAD0_opsz24.png",
            "settings": icons_path / "settings_24dp_FILL0_wght400_GRAD0_opsz24.png",
        })
        asset.load_all_images()

    @unittest.skipIf(os.name != 'nt', "Skipping The OS is not Windows")
    def test_app_starts_within_3_seconds(self):
        """
        アプリの起動時間が3秒未満
        """
        sw = Stopwatch.start_new()

        test_app = MyApp()
        test_app.after_launch([str(self.image_path)])  # ここでアプリの起動をシミュレート

        elapsed = sw.elapsed
        print(f"{elapsed:.3f}", end=None)
        self.assertTrue(elapsed < 3, f"App launch time was {elapsed:.3f} seconds, which is longer than the threshold.")


if __name__ == "__main__":
    unittest.main()
