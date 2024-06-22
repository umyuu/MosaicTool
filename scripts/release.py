# -*- coding: utf-8 -*-
"""
    release
"""
from dataclasses import dataclass, field
from datetime import datetime
import glob
import hashlib
import os
from pathlib import Path
import sys
import time
import zipfile

# プロジェクトのルートディレクトリをシステムパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import PROGRAM_NAME, get_package_version
from src.utils import Stopwatch

__version__ = get_package_version()


def hash_compute(file_path: Path) -> str:
    """
    ファイルのハッシュ値を計算します。
    :param file_path: 計算対象のファイル
    :return: ハッシュ値 (大文字)
    """
    # ハッシュ値の種類を選択（ここではSHA-256を使用）
    hash_algorithm = hashlib.sha256()
    # ファイルをバイナリモードで開いてハッシュ値を計算
    with file_path.open('rb') as file:
        # ファイルからデータを読み込んでハッシュ値を更新
        while chunk := file.read(4096):
            hash_algorithm.update(chunk)

    # ハッシュ値の16進数表現を取得
    return hash_algorithm.hexdigest().upper()


def create_readMe(file1_path: Path, file2_path: Path, hash_value: str, output_path: Path):
    """
    Zipファイルに添付するReadMe.txtを作成します。

    :param file1_path: ReadMe.md
    :param file2_path: handouts.txt
    :param hash_value: ハッシュ値。
    :param output_path: 出力先。
    """
    # 現在の日付を取得
    current_date = datetime.now()
    # 8桁の日付文字列にフォーマット
    date_string = current_date.strftime("%Y/%m/%d")

    readme_content = ""
    readme_content = f"{date_string} ver {__version__}  \n" 
    readme_content += file1_path.read_text("utf-8")
    readme_content += "\n\n"
    readme_content += "## ハッシュ値  \n"
    readme_content += f"{PROGRAM_NAME}.exe Hash Value (SHA-256): {hash_value}\n"
    readme_content += file2_path.read_text("utf-8")

    output_path.write_text(readme_content, "utf-8")


def create_zip(folder_path: Path, output_zip: Path, additional_files_with_names: dict[Path, str]) -> int:
    """
    引数で指定されたフォルダとファイルをZIPファイルに格納します。

    :param folder_path: ZIPファイルに含めるフォルダ。
    :param output_zip: 出力するZIPファイルのパス。
    :param additional_files_with_names: 追加ファイルとその保存名の辞書。
    :return: ZIPファイルに追加されたファイルの数。
    """
    count: int = 0

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(folder_path)
                zip_file.write(file_path, arcname)
                print(arcname)
                count += 1

        for file_path, save_name in additional_files_with_names.items():
            print(file_path)
            zip_file.write(file_path, arcname=save_name)
            count += 1

    return count


@dataclass(frozen=True)
class SetupConfigRation:
    """
    セットアップ設定
    """
    source_dir: Path = Path("dist")
    output_zip: Path = source_dir / f"{PROGRAM_NAME}.zip"
    app_file: Path = source_dir / f"{PROGRAM_NAME}/{PROGRAM_NAME}.exe"
    handouts_file: Path = source_dir / "handouts.txt"
    exclude_files: list[Path] = field(default_factory=list)


def main():
    sw = Stopwatch.start_new()
    # Configuration
    config = SetupConfigRation()
    # 除外するファイル
    config.exclude_files.extend([config.output_zip, config.source_dir / ".gitignore", config.handouts_file])
    # zipファイルに追加するファイル

    readme = config.source_dir / "ReadMe.txt"
    additional_files_with_names = {
        readme: readme.name,
        Path("docs/initial_screen.png"): "initial_screen.png",
        Path(f"{PROGRAM_NAME}.json"): f"sample/{PROGRAM_NAME}.json",
    }

    hash_value = hash_compute(config.app_file)
    print(f"Compute hash, ({sw.elapsed:.3f}s)")

    create_readMe(Path("ReadMe.md"), config.handouts_file, hash_value, readme)
    print(f"Created ReadMe.txt, ({sw.elapsed:.3f}s)")

    count: int = create_zip(config.source_dir / str(f"{PROGRAM_NAME}"), config.output_zip, additional_files_with_names)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Release zip file created at: {config.output_zip} on {current_time}")
    print(f"  Store total:{count}, ({sw.elapsed:.3f}s)")


if __name__ == '__main__':
    main()
