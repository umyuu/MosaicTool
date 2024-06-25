# 🌟 MosaicTool — プログラム初心者向け開発環境構築ガイド  
## 📚 概要  
このガイドは、プログラム初心者の方がMosaicToolの開発環境をセットアップし、ソースコードから実行ファイルを作成する手順を説明します。  

## 作業手順  
大きく「開発環境のセットアップ」と「実行ファイルの作成」の２つに分かれます。
1. [開発環境のセットアップ](#1-開発環境のセットアップ)  
1. [実行ファイルの作成](#2-実行ファイルの作成)  

## 1. 開発環境のセットアップ  
必要なツールをインストールします。  

### 💻 VSCodeのインストール  
- Visual Studio Code (VSCode) をインストールします。以下のリンクからダウンロードしてください。  
https://code.visualstudio.com/Download  

### 🐍 Pythonのインストール  
- Pythonをインストールします。以下のリンクからダウンロードしてください。  
https://www.python.org/downloads/  
インストール時に、「Add Python to PATH」のチェックボックスを必ずチェックしてください。 これにより、Pythonがコマンドラインから実行できるようになります。  

### 📦 MosaicToolのソースコードのセットアップ  
  - [Releases](https://github.com/umyuu/MosaicTool/releases)ページを開き、一番上の Assets 欄にある `Source code(zip)` をダウンロードします。  
  - ダウンロードしたzipファイルを展開します。  
### ▶️ 開発環境を作成する  
  1. 展開した MosaicTool のフォルダ内の scripts フォルダを開きます。  
  1. `setup_dev_env.bat`をダブルクリックで実行します。これにより実行ファイル作成に必要な開発環境が作成されます。  

## 2. 実行ファイルの作成  
## ▶️ VSCodeで実行ファイルを作成する  
  1. VSCodeを開きます。  
  1. メニューから「フォルダーを開く」を選択し、展開した MosaicTool フォルダを指定して開きます。  
  1. 左側の「実行とデバック」(Ctrl+Shift+Dキー)を押します。  
  1. 緑の▷矢印の横のドロップダウンより「Build」を選択します。  
  1. 実行ボタン(F5キー)を押すと実行ファイルの作成処理を開始します。  
  1. 正常に終了すると、 dist\MosaicTool フォルダに MosaicTool.exe ファイルを作成します。  
  >  **正常終了時の判断方法**  
  >  以下のメッセージが画面下のターミナル欄に表示されます。  
  >  Build has completed successfully. Please check the folder.:dist\MosaicTool  

## ❓ よくある質問  
Q1. 実行ファイルを作成時にアンチウィルスソフトで検知された。  
A1. ブートローダーを再作成してください。  
私以外が作成された、noteの記事を参考にしてください。  
https://note.com/tkvier/n/nd6e4f6eb7033  
MinGW-W64のセットアップが終了後：  
  a.  MosaicTool フォルダ内の scripts フォルダを開きます。  
  b. `setup_build.bat`をダブルクリックします。  
  c. 黒い画面に実行確認メッセージが表示されます。Yを入力しEnterキーを押します。これによりブートローダーが再作成されます。  
  d. その後、再度[実行ファイルの作成](#2-実行ファイルの作成)を行ってください。  
