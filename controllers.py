# -*- coding: utf-8 -*-
"""
    AppController
"""
from pathlib import Path

from lib.models import DataModel, StatusMessage, MosaicImageFile


class AppController:
    """
    コントローラー
    """
    def __init__(self, model: DataModel, view, fnc):
        self.model = DataModel()
        self.view = view
        self.fnc = fnc

    def add_file_path(self, file_path: str) -> int:
        """
        ファイルをデータモデルに追加します。
        パスがディレクトリの場合は、ディレクトリ内のファイルも追加します。
        :return: 追加件数
        """
        path = Path(file_path)
        count: int = 0
        if path.is_dir():
            for f in path.glob("*.*"):
                count += self.model.add_file_path(f)
        else:
            count += self.model.add_file_path(path)
        return count

    def handle_drop(self, event):
        """
        ドロップイベント
        """
        count: int = 0
        if event.data:
            self.model.clear()
            file_paths = event.data.split('\n')  # 改行で分割
            for file_path in file_paths:
                for f in file_path.split():
                    if f.strip():  # 空でないパスを処理
                        print(f"Processing file path: {f}")
                        count += self.add_file_path(f)
            print(self.model)
            if self.model.count() > 0:
                self.display_image()
            self.view.status_message(f"received in drop event files:{count}")
        else:
            self.view.status_message("No data received in drop event")

    def handle_pick_images(self):
        """
        ファイル選択ボタンクリック時
        """
        self.view.on_select_files(None)

    def handle_back_images(self):
        """
        前の画像に遷移するをクリック時
        """
        self.model.prev_index()
        self.display_image()

    def handle_forward_images(self):
        """
        次の画像に遷移するをクリック時
        """
        self.model.next_index()
        self.display_image()

    def display_image(self):
        """
        画面に画像を表示します。
        """
        file = self.model.get_current_file()
        self.view.display_image(file)

    def handle_select_files_complete(self, files: tuple[str, ...]):
        """
        ファイル選択ダイアログよりファイル選択時
        """
        count: int = 0
        self.model.clear()
        for file_path in files:
            count += self.add_file_path(file_path)
        if count > 0:
            self.view.status_message(f"select files:{count}")
        else:
            self.view.status_message("No data file select")

    def get_new_file(self) -> Path:
        """
        モザイク適用後のファイル名を生成します。
        :return: Path
        """
        f = self.model.get_current_file()
        return MosaicImageFile.newFileName(f)

    def set_window_title(self, text: str):
        """
        タイトルバーの設定
        """
        self.fnc(text)

    def get_status(self) -> StatusMessage:
        """
        ステータスメッセージを取得します。
        """
        files = self.model.get_file_paths()
        total = len(files)
        if total == 0:
            return StatusMessage()

        filepath = self.model.get_current_file()
        width, height = MosaicImageFile.get_image_size(filepath)

        m = MosaicImageFile(str(filepath))

        return StatusMessage(
            current=self.model.current + 1,
            total=total,
            mtime=m.mtime,
            file_size=m.st_size,
            width=width,
            height=height
        )
