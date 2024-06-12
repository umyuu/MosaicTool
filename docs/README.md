# 🌟 MosaicTool — プログラム初心者向け開発環境構築ガイド  
## 📚 概要  
このガイドは、プログラム初心者の方がMosaicToolの開発環境をセットアップし、ソースコードから実行する手順を説明します。  
## 🛠️ 開発環境のセットアップ  
必要なツールをインストールします。  

### 💻 VSCodeのインストール  
- Visual Studio Code (VSCode) をインストールします。以下のリンクからダウンロードしてください。  
https://code.visualstudio.com/Download  

### 🐍 Pythonのインストール  
- Pythonをインストールします。以下のリンクからダウンロードしてください。  
https://www.python.org/downloads/  
インストール時に、「Add Python to PATH」のチェックボックスを必ずチェックしてください。 これにより、Pythonがコマンドラインから実行できるようになります。  

### 📦 MosaicToolのセットアップ  
  - [Releases](https://github.com/umyuu/MosaicTool/releases)ページを開き、一番上の Assets 欄にある `Source code(zip)` をダウンロードします。  
  - ダウンロードしたzipファイルを展開します。  

## ▶️ VSCodeで実行する  
  1. VSCodeを開きます。  
  1. メニューから「フォルダーを開く」を選択し、展開した MosaicTool フォルダを指定して開きます。  
  1. 左側の「実行とデバック」(Ctrl+Shift+Dキー)を押します。  
  1. 緑の▷矢印の横のドロップダウンより「Run app」を選択します。  
  1. 実行ボタン(F5キー)を押します。  

## ▶️ VSCodeでビルドする  
  1. VSCodeを開きます。  
  1. メニューから「フォルダーを開く」を選択し、展開した MosaicTool フォルダを指定して開きます。  
  1. 左側の「実行とデバック」(Ctrl+Shift+Dキー)を押します。  
  1. 緑の▷矢印の横のドロップダウンより「Build」を選択します。  
  1. 実行ボタン(F5キー)を押すとbuildが開始します。  
  1. ビルドが正常に終了すると、distフォルダに MosaicTool.exe ファイルが作成されます。  
  >  **正常終了時の判断方法**  
  >  以下のメッセージが画面下のターミナル欄に表示されます。  
  >  Fixing EXE headers
  >  INFO: Building EXE from EXE-00.toc completed successfully.  

## ❓ よくある質問  
1. エラーメッセージ:`ConnectionRefusedError: [WinError 10061] 対象のコンピューターによって拒否されたため、接続できませんでした。`  
対処法: 5秒ぐらい待った後に、もう一度実行(F5キー)してください。  

1. ビルド時にアンチウィルスソフトで検知された。  
私以外が作成された、noteの以下の記事をブートローダーを作り替えてください。  
https://note.com/tkvier/n/nd6e4f6eb7033  
その後、再度ビルドを行ってください。  
