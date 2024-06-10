# -*- coding: utf-8 -*-
"""
    release
"""
from dataclasses import dataclass, field
from datetime import datetime
import glob
import hashlib
from pathlib import Path
import time
from typing import List
import zipfile

__version__ = "0.0.2"


def hash_compute(file_path: Path) -> str:
    """
    ハッシュ値を計算するファイル
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

    # 現在の日付を取得
    current_date = datetime.now()
    # 8桁の日付文字列にフォーマット
    date_string = current_date.strftime("%Y/%m/%d")

    readme_content = ""
    readme_content = f"{date_string} ver {__version__}  \n" 
    readme_content += file1_path.read_text("utf-8")
    readme_content += "\n\n"
    readme_content += "## ハッシュ値  \n"
    readme_content += f"MosaicTool.exe Hash Value (SHA-256): {hash_value}\n"
    readme_content += file2_path.read_text("utf-8")

    output_path.write_text(readme_content, "utf-8")


def get_compressible_files(root_dir: Path, exclude_files: List[Path]) -> List[Path]:
    """
    圧縮対象のファイル一覧を取得します。

    Args:
        root_dir (Path): 圧縮したいディレクトリのパス。
        exclude_file (str): 除外するファイルの名前。

    Returns:
        list: 圧縮対象のファイルパスのリスト。
    """
    compressible_files: List[Path] = []

    for file_path in glob.glob(str(root_dir) + "/*.*"):
        file_path = Path(file_path)  # 文字列からPathに変換
        if not any(file_path.samefile(exclude_file) for exclude_file in exclude_files if exclude_file.exists()):
            compressible_files.append(file_path)

    return compressible_files


def create_zip(source_dir: List[Path], output_zip: Path) -> int:
    """
    ディレクトリ内のすべてのファイルをZIPに追加し、指定されたファイルを除外します。

    Args:
        source_dir (Path): 圧縮したいディレクトリのパス。
        output_zip (Path): 出力するZIPファイルのパス。

    Returns:
        int: ZIPに追加されたファイルの数。
    """
    count: int = 0

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_dir:
            print(file_path)
            zipf.write(file_path, arcname=file_path.name)
            count += 1

    return count


@dataclass
class SetupConfigRation:
    source_dir: Path = Path("dist")
    output_zip: Path = source_dir / "MosaicTool.zip"
    app_file: Path = source_dir / "MosaicTool.exe"
    handouts_file: Path = source_dir / "handouts.txt"
    exclude_files: List[Path] = field(default_factory=list)
    additional_files: List[Path] = field(default_factory=list)


def main():
    start: float = time.perf_counter()
    # Configuration
    config = SetupConfigRation()
    config.exclude_files.extend([config.output_zip, config.source_dir / ".gitignore", config.handouts_file])
    config.additional_files.extend([
        Path("docs/initial_screen.png"),
    ])

    # List of additional files to include in the zip
    hash_value = hash_compute(config.app_file)
    print(f"Compute hash, ({time.perf_counter() - start:.3f}s)")

    create_readMe(Path("ReadMe.md"), config.handouts_file, hash_value, config.source_dir / "ReadMe.txt")
    print(f"Created ReadMe.txt, ({time.perf_counter() - start:.3f}s)")

    compressible_files = get_compressible_files(config.source_dir, config.exclude_files) + config.additional_files
    print(f"Get_compressible_files, ({time.perf_counter() - start:.3f}s)")
    count: int = create_zip(compressible_files, config.output_zip)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Release zip file created at: {config.output_zip} on {current_time}")
    print(f"  Store total:{count}, ({time.perf_counter() - start:.3f}s)")


if __name__ == '__main__':
    main()
