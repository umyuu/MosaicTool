"""
Modelの単体テスト
"""
import os
import sys
from typing import List
import unittest

from PIL import Image, ImageDraw, ImageChops

# プロジェクトのルートディレクトリをシステムパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.effects.image_effects import MosaicEffect


class TestMosaicFilter(unittest.TestCase):
    """
    MosaicFilterのテストクラス
    """
    def setUp(self):
        """テストのセットアップを行います。"""
        self.current_dir = os.path.dirname(__file__)

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
                cell_size = MosaicEffect.calc_cell_size(image)
                actual.append(cell_size)
        self.assertListEqual([4, 8, 13, 41], actual, )

    def create_gradient_image(self, width: int, height: int) -> Image.Image:
        """
        グラデーション画像を作成します
        :param width: 画像の幅
        :param height: 画像の高さ
        :return: グラデーション画像
        """
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)

        for i in range(width):
            color = int(255 * (i / width))
            draw.line((i, 0, i, height), fill=(color, color, color))

        return image

    def test_mosaic_effect_compare_images(self):
        """
        モザイクエフェクト。
        """
        cell_sizes: List[int] = [4, 8, 10, 13, 16, 20, 41]

        for cell_size in cell_sizes:
            actual_image_path = os.path.join(self.current_dir, 'test_files', f'mosaic_cell_size_{cell_size}.png')
            # 正解の画像
            with Image.open(actual_image_path) as actual_image:
                # グラデーション画像を生成
                width: int = 256
                height: int = 256
                with self.create_gradient_image(width, height) as gradient_image:
                    # グラデーション画像を保存（テスト用、任意）
                    #gradient_image.save(f'gradient_image{cell_size}.png')

                    # MosaicEffectを初期化
                    mosaic_effect = MosaicEffect(cell_size)
                    # モザイクエフェクトを適用
                    mosaic_effect.apply(gradient_image, 0, 0, width, height)

                    result: bool = self.compare_images(gradient_image, actual_image)
                    test_image_file = f'mosaic_image_{mosaic_effect.cell_size}.png'
                    if not result:  # モザイク画像を保存（テスト用）
                        gradient_image.save(test_image_file)
                    self.assertTrue(result, f"test:{test_image_file}, actual:{actual_image_path}")

    def compare_images(self, image1: Image.Image, image2: Image.Image, diff_image_path=None) -> bool:
        """
        2つの画像を比較し、差分を計算します
        :param image1: 1つ目の画像
        :param image2: 2つ目の画像
        :param diff_image_path: 差分画像を保存するパス（省略可能）
        :return: 差分比較結果 差分なしは、true、それ以外は、false
        """
        # 差分を計算
        diff = ImageChops.difference(image1, image2)

        # 差分をピクセル単位で取得
        diff_data = diff.getdata()
        if diff_data is None:
            raise ValueError()

        # 差分の合計を計算
        diff_sum = sum(sum(pixel) for pixel in diff_data)

        # 差分画像を保存（オプション）
        if diff_image_path:
            diff.save(diff_image_path)
        return diff_sum == 0


if __name__ == "__main__":
    unittest.main()
