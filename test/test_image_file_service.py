"""
ImageFileServiceの単体テスト
"""
import os
from pathlib import Path
import sys
import unittest

from PIL import Image

# プロジェクトのルートディレクトリをシステムパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.image_file_service import ImageFileService


class TestImageFileService(unittest.TestCase):
    """
    ImageFileServiceのテストクラス
    """
    def setUp(self):
        """テストのセットアップを行います。"""
        self.current_dir = os.path.dirname(__file__)

    def test_save_png_metadata(self):
        """
        PNGINFOの出力確認
        """
        image_path = os.path.join(self.current_dir, 'test_files', 'pnginfo_valid.png')
        # テストに使用する画像と出力先パスを準備
        with Image.open(image_path) as src_image:
            out_image = Image.new("RGB", (100, 100), color="blue")
            output_path = Path("test_output.png")

            # テスト用のPNG情報を準備
            # Todo:dpiはタプルが正常値。暫定対応。PNGINFOでは読めます。
            # {'srgb': 0, 'gamma': 0.45455, 'dpi': (96.012, 96.012)}
            png_info = {
                "srgb": "0",
                "gamma": "0.45455",
                "dpi": "96.012, 96.012"
            }
            # ImageFileService の save_png_metadata メソッドを呼び出す
            ImageFileService.save_png_metadata(src_image, out_image, output_path)

            # 出力先ファイルを開いて PNG 情報を取得
            actual_info = ImageFileService.get_image_info(output_path)
            # 期待される PNG 情報と実際の PNG 情報が一致することを検証
            self.assertEqual(actual_info, png_info)

            # テスト完了後に出力先ファイルを削除
            output_path.unlink()


if __name__ == "__main__":
    unittest.main()
