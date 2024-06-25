# -*- coding: utf-8 -*-
"""
    build
"""
import subprocess
import sys
from pathlib import Path


def main():
    args = [
        "pyinstaller",
        *sys.argv[1:]
    ]
    subprocess.run(args, check=True)
    path = Path("dist/MosaicTool")
    print(f"Build has completed successfully. Please check the folder.:{str(path)}")


if __name__ == '__main__':
    main()
