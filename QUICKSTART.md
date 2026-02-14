# 🚀 クイックスタートガイド

## インストール（初回のみ）

PowerShellを開いて、以下を実行:

```powershell
pip install streamlit plotly pandas requests matplotlib
```

## 起動方法

### 方法1: バッチファイル（Windows）

`run_ui.bat` をダブルクリック

### 方法2: コマンドライン

```powershell
streamlit run potato_farming_ui.py
```

## アクセス

ブラウザが自動的に開きます。
開かない場合は、以下のURLにアクセス:

```
http://localhost:8501
```

## 基本的な使い方

1. 左のサイドバーで設定
   - 緯度・経度を入力（例: 北海道 = 43.06, 141.35）
   - 植え付け日を選択
   
2. 「🌐 データ取得」ボタンをクリック

3. グラフと推奨事項が表示されます

## 終了方法

- コマンドプロンプト/PowerShellで `Ctrl+C`
- またはブラウザを閉じる

## トラブルシューティング

### エラー: "streamlit: 用語が認識されません"

```powershell
pip install streamlit
```

### エラー: "ポートが使用中"

```powershell
streamlit run potato_farming_ui.py --server.port 8502
```

### ブラウザが開かない

手動で開く: http://localhost:8501

---

詳しくは `README_UI.md` を参照してください。
