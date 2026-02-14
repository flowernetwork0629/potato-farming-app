# 🥔 じゃがいも農業管理システム - Streamlit UI版

NASA POWER APIを使用した、インタラクティブなWebダッシュボードです。

## ✨ 特徴

### 主な機能
- 🌍 **地図表示**: 農場の位置を地図上で確認
- 📊 **リアルタイムグラフ**: インタラクティブな気象データの可視化
- 💡 **自動推奨**: 気象条件に基づいた栽培アドバイス
- 📈 **統計ダッシュボード**: 重要な指標を一目で確認
- 📥 **データエクスポート**: CSV形式でデータをダウンロード
- 🎨 **美しいUI**: 直感的で使いやすいインターフェース

## 🚀 インストール

### 1. 必要なパッケージをインストール

```powershell
pip install -r requirements_ui.txt
```

または個別にインストール:

```powershell
pip install streamlit plotly pandas requests matplotlib
```

## 💻 使い方

### アプリケーションの起動

```powershell
streamlit run potato_farming_ui.py
```

起動すると、ブラウザが自動的に開き、以下のURLでアプリにアクセスできます:
```
http://localhost:8501
```

### 基本的な使い方

1. **サイドバーで設定を行う**
   - API キー（デフォルト値が入力済み）
   - 農場の緯度・経度を入力
   - 植え付け日を選択
   - データ取得日数を設定（30-180日）

2. **データを取得**
   - 「🌐 データ取得」ボタンをクリック
   - NASA APIからリアルタイムデータを取得

3. **結果を確認**
   - 地図上で農場の位置を確認
   - 現在の成長ステージを表示
   - 栽培推奨事項を確認
   - インタラクティブなグラフで気象データを分析
   - 詳細データをテーブルで確認

4. **データをエクスポート**
   - 「📥 CSVダウンロード」ボタンでデータを保存

## 📊 表示されるグラフ

### 1. 気温トレンド
- 平均気温、最高気温、最低気温
- 最適温度範囲（10-25°C）の表示

### 2. 降水量
- 日別の降水量を棒グラフで表示

### 3. 相対湿度
- 湿度の推移
- 高リスクライン（85%）の表示

### 4. 日射量
- 太陽放射量の推移

## 💡 推奨事項の内容

アプリは以下の条件を自動評価し、推奨事項を表示します:

### 気温評価
- ✅ **適正**: 10-25°C
- ⚠️ **低温警告**: 10°C未満（霜害リスク）
- ⚠️ **高温警告**: 25°C以上（高温ストレス）

### 水分評価
- ✅ **適正**: 週間降水量 15-50mm
- 💧 **水分不足**: 15mm未満（灌漑必要）
- ☔ **過湿注意**: 50mm以上（病害リスク）

### 湿度評価
- ✅ **適正**: 85%未満
- 🦠 **病害リスク**: 85%以上（疫病リスク）

### 成長ステージ別アドバイス
各成長ステージに応じた具体的な管理方法を提示

## 🔧 カスタマイズ

### 農場の位置を変更

サイドバーで緯度・経度を入力:
```
緯度: 35.6812 (東京の例)
経度: 139.7671
```

日本の主要都市の座標:
- 札幌: (43.06, 141.35)
- 東京: (35.68, 139.77)
- 大阪: (34.69, 135.50)
- 福岡: (33.59, 130.40)

### データ取得期間の調整

スライダーで30日〜180日の範囲で設定可能

### 成長ステージの調整

`potato_farming_ui.py`の以下の部分を編集:

```python
self.growth_stages = {
    "発芽期": (0, 21),
    "栄養成長期": (21, 50),
    # ... カスタマイズ
}
```

## 🌐 ネットワーク設定

### ファイアウォール設定

Streamlitはデフォルトでポート8501を使用します。
別のポートを使用する場合:

```powershell
streamlit run potato_farming_ui.py --server.port 8080
```

### 外部アクセスを許可

```powershell
streamlit run potato_farming_ui.py --server.address 0.0.0.0
```

## 📱 スマートフォン対応

このアプリはレスポンシブデザインで、スマートフォンやタブレットからもアクセス可能です。

同じネットワーク内であれば、以下のURLでアクセス:
```
http://[PCのIPアドレス]:8501
```

## 🐛 トラブルシューティング

### Streamlitが起動しない

```powershell
# Streamlitを再インストール
pip uninstall streamlit
pip install streamlit
```

### ブラウザが自動的に開かない

手動でブラウザを開き、以下のURLにアクセス:
```
http://localhost:8501
```

### APIエラーが発生する

- インターネット接続を確認
- APIキーが正しいか確認
- 日付範囲が正しいか確認（未来の日付は指定できません）

### グラフが表示されない

```powershell
# Plotlyを再インストール
pip install --upgrade plotly
```

### ポートが使用中

別のポートで起動:
```powershell
streamlit run potato_farming_ui.py --server.port 8502
```

## 🎨 UIのカスタマイズ

### テーマの変更

`.streamlit/config.toml`ファイルを作成:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### カスタムCSS

`potato_farming_ui.py`の`st.markdown`セクションでCSSを編集

## 📊 データの保存

### セッションの保持

Streamlitはセッション中のデータを自動的に保持します。
ブラウザを更新すると、データは保持されたままになります。

### データベース連携（オプション）

SQLiteやPostgreSQLと連携してデータを永続化することも可能です。

## 🚀 本番環境へのデプロイ

### Streamlit Cloud（無料）

1. GitHubにコードをプッシュ
2. https://streamlit.io/cloud にアクセス
3. リポジトリを接続
4. デプロイ

### Herokuへのデプロイ

`Procfile`を作成:
```
web: streamlit run potato_farming_ui.py --server.port $PORT
```

### Dockerでのデプロイ

`Dockerfile`の例:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements_ui.txt .
RUN pip install -r requirements_ui.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "potato_farming_ui.py"]
```

## 🔐 セキュリティ

### APIキーの保護

本番環境では、APIキーを環境変数で管理:

```python
import os
api_key = os.getenv("NASA_API_KEY", "デフォルト値")
```

PowerShellで環境変数を設定:
```powershell
$env:NASA_API_KEY = "your_api_key_here"
```

## 📝 ライセンス

このアプリケーションは教育・研究目的で自由に使用できます。

## 🤝 貢献

改善案やバグ報告は歓迎します！

## 📞 サポート

問題が発生した場合は、以下を確認してください:
- Python 3.7以上がインストールされているか
- 必要なパッケージがすべてインストールされているか
- インターネット接続が安定しているか

---

**作成日**: 2025年2月
**バージョン**: 2.0.0（UI版）
