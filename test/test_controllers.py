"""
AppControllerの単体テスト
"""
from dataclasses import dataclass
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

# プロジェクトのルートディレクトリをシステムパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.controllers import AppController
from src.models import AppDataModel
from src.widgets import MainPage
from src.app_config import AppConfig


class TestAppController(unittest.TestCase):
    def setUp(self):
        """テストのセットアップを行います。"""
        self.controller = AppController(AppDataModel(Mock(AppConfig)), Mock(MainPage), Mock())

        # on_update_process_time メソッドをモックに追加
        self.controller.view.on_update_process_time = Mock()

    """コントローラーのテストクラス"""
    @unittest.skipIf(os.name != 'nt', "Skipping The OS is not Windows")
    def test_drop_file_parser(self):
        """
        ドラッグ＆ドロップのパス解析
        """
        current_dir = Path(__file__).parent
        assets = [
            str(current_dir / "test_files/.gitignore"),
            str(current_dir / "test_files/jet_256x256.webp"),
            str(current_dir / "test_files/pnginfo_valid.png"),
            # 日本語ファイル名の場合
            "{" + str(current_dir / "test_files/pnginfo_valid.png") + "}",
        ]

        @dataclass
        class Event:
            data: str

        event = Event(' '.join(assets))
        self.controller.handle_drop(event)

        count = self.controller.model.count
        # 画像ファイルではない、.gitignoreは処理をスキップします。
        # 結果の件数は、3と比較します。
        self.assertTrue(count == 3, f"test_drop_file_parser error {count}")


if __name__ == "__main__":
    unittest.main()
