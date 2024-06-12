"""
AppControllerの単体テスト
"""
from dataclasses import dataclass
import sys
import os
import unittest
from unittest.mock import Mock
from pathlib import Path

# プロジェクトのルートディレクトリをシステムパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.controllers import AppController
from src.models import DataModel
from src.widgets import MainPage


class TestAppController(unittest.TestCase):
    """コントローラーのテストクラス"""
    @unittest.skipIf("DISPLAY" not in os.environ, "Skipping GUI test on headless environment")
    def test_drop_file_parser(self):
        """
        ドラッグ＆ドロップのパス解析
        """
        current_dir = Path(__file__).parent
        assets = [
            str(current_dir / "test_files/.gitignore"),
            str(current_dir / "test_files/jet_256x256.webp"),
            str(current_dir / "test_files/test_image_png_pnginfo_valid.png"),
            # 日本語ファイル名の場合
            "{" + str(current_dir / "test_files/test_image_png_pnginfo_valid.png") + "}",
        ]

        @dataclass
        class Event:
            data: str

        model = DataModel()
        main_page = Mock(MainPage)

        controller = AppController(model, main_page, self.dummy_func)
        event = Event(' '.join(assets))

        controller.handle_drop(event)
        count = controller.model.count()
        # 画像ファイルではない、.gitignoreは処理をスキップします。
        # 結果の件数は、3と比較します。
        self.assertTrue(count == 3, f"test_drop_file_parser error {count}")

    def dummy_func(self, text: str):
        pass


if __name__ == "__main__":
    unittest.main()
