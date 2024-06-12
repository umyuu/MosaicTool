"""
Modelの単体テスト
"""
import sys
import os
import unittest
from PIL import Image
from typing import List

# プロジェクトのルートディレクトリをシステムパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import MosaicFilter


class TestMosaicFilter(unittest.TestCase):
    """
    MosaicFilterのテストクラス
    """
    def test_mosaic_size(self):
        """
        モザイクサイズの計算
        """
        # 画像の幅, 高さ
        image_sizes = [
            (300, 200),  # 最小モザイク数は、4
            (800, 600),
            (1280, 1024),
            (2894, 4093),  # A4 350dpi 210x297  2,893.70x4,092.5
        ]

        actual: List[int] = []
        for size in image_sizes:
            with Image.new("RGBA", size, color="blue") as image:
                mosaic = MosaicFilter(image)
                actual.append(mosaic.cell_size)
        self.assertListEqual([4, 8, 13, 41], actual, )


if __name__ == "__main__":
    unittest.main()
