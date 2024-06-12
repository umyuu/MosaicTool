# -*- coding: utf-8 -*-
"""
    build
"""
import subprocess
import sys


def main():
    args = [
        "pyinstaller",
        *sys.argv[1:]
    ]
    subprocess.run(args, check=True)


if __name__ == '__main__':
    main()
