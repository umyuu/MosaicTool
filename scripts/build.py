# -*- coding: utf-8 -*-
"""
    build
"""
import subprocess
import sys


def main():
    args = sys.argv[1:]
    subprocess.run([sys.executable] + args, check=True)


if __name__ == '__main__':
    main()
