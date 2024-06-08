# -*- coding: utf-8 -*-
"""
    MosaicTool
"""
from functools import partial
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image

PROGRAM_NAME = 'MosaicTool'
__version__ = '0.0.1'


class HeaderFrame(tk.Frame):
    def __init__(self, master, bg):
        super().__init__(master, bg=bg)
        self.createWidgets()

    def createWidgets(self):
        self.widgetHeader = tk.Label(self, text="ヘッダーはここ", font=("", 10))
        self.widgetHeader.pack()
        self.btn_select_file = tk.Button(self, text="ファイル選択(F)", command=partial(self.on_select_file, event=None)) 
        self.btn_select_file.pack()

    def on_select_file(self, event):
        # 画像形式
        ImageFormat = {
            'PNG': ('*.png', ),
            'JPEG': ('*.jpg', '*.jpeg', ),
            'WEBP': ('*.webp', ),
            'BMP': ('*.bmp', ),
            'PNM': ('*.pbm', '*.pgm', '*.ppm', )
        }
        IMAGE_FILE_TYPES = [
            ('Image Files', ImageFormat['PNG'] + ImageFormat['JPEG'] + ImageFormat['WEBP'] + ImageFormat['BMP']),
            ('png (*.png)', ImageFormat['PNG']),
            ('jpg (*.jpg, *.jpeg)', ImageFormat['JPEG']),
            ('webp (*.webp)', ImageFormat['WEBP']),
            ('bmp (*.bmp)', ImageFormat['BMP']),
            ('*', '*.*')
        ]
        print('on_select_file...')
        return filedialog.askopenfilename(parent=self, filetypes=IMAGE_FILE_TYPES)


class MainFrame(tk.Frame):
    def __init__(self, master, bg):
        super().__init__(master, bg=bg)

        self.textbox = tk.Text(self)
        self.textbox.insert(0.0, "Drag and drop your image")
        self.textbox.configure(state='disabled')

        # スクロールバー
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.textbox.yview)
        self.textbox['yscrollcommand'] = self.scrollbar.set

        self.textbox.grid(column=0, row=0, sticky=tk.E + tk.W + tk.S + tk.N)
        self.scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


class FooterFrame(tk.Frame):
    def __init__(self, master, bg):
        super().__init__(master, bg=bg)
        self.createWidgets()

    def createWidgets(self):
        widgetFooter = tk.Label(self, text="フッターはここ", font=("", 10))
        widgetFooter.pack(expand=True)
        return


class MainPage(tk.Frame):
    def __init__(self):
        super().__init__(bg="#00C8B4")
        self.HeaderFrame = HeaderFrame(self, bg="#44F7D3")
        self.HeaderFrame.grid(column=0, row=0, sticky=(tk.E + tk.W + tk.S + tk.N))
        self.MainFrame = MainFrame(self, bg="#88FFEB")
        self.MainFrame.grid(column=0, row=1, sticky=(tk.E + tk.W + tk.S + tk.N))
        self.FooterFrame = FooterFrame(self, bg="#FFBB9D")
        self.FooterFrame.grid(column=0, row=2, sticky=(tk.E + tk.W + tk.S + tk.N))
        self.columnconfigure(0, weight=1)  # ヘッダーをウィンドウ幅まで拡張する


class MyApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        width = 640
        height = 480
        self.title(PROGRAM_NAME)
        self.geometry(f'{width}x{height}')  # ウィンドウサイズ
        self.minsize(width, height)

        self.frame_drag_drop = MainPage()
        # ドラッグアンドドロップ
        self.frame_drag_drop.drop_target_register(DND_FILES)
        self.frame_drag_drop.dnd_bind('<<Drop>>', self.onDragAndDrop)
        #self.frame_drag_drop.pack(expand=True)
        self.frame_drag_drop.grid(column=0, row=0, sticky=tk.E + tk.W + tk.S + tk.N)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def onDragAndDrop(self, e):
        message = '\n' + e.data
        text = self.frame_drag_drop.MainFrame.textbox
        text.configure(state='normal')
        text.insert(tk.END, message)
        text.configure(state='disabled')

        text.see(tk.END)

        image = Image.open(e.data)
        image.show()


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
