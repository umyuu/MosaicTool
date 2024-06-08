# -*- coding: utf-8 -*-
"""
    PhotoImageButton
"""
import tkinter as tk


class PhotoImageButton(tk.Button):
    """
    イメージボタンクラス
    """
    def __init__(self, master=None, image_path="", command=None, **kwargs):
        img = tk.PhotoImage(file=image_path)
        img = img.subsample(3, 3)
        if command is None:
            super().__init__(master, image=img, compound="top", **kwargs)
        else:
            super().__init__(master, image=img, compound="top", command=command, **kwargs)

        self.img = img  # Keep a reference to the image to prevent it from being garbage collected
