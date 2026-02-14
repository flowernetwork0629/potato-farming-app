#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
じゃがいも農業管理アプリケーション - Streamlit UI版
NASA POWER APIを使用した対話的なWebダッシュボード
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json

# ページ設定
st.set_page_config(
    page_title="🥔 じゃがいも農業管理システム",
    page_icon="🥔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .recommendation-box {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 10px 0;
    }
    .stage-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


class PotatoFarmManagerUI:
    """じゃがいも農場管理クラス（UI版）"""
    
    def __init__(self, api_key: str, latitude: float, longitude: float):
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        
        # じゃがいもの成長ステージ（日数）
        self.growth_stages = {
            "発芽期": (0, 21),
            "栄養成長期": (21, 50),
            "塊茎形成期": (50, 80),
            "塊茎肥大期": (80, 110),
            "成熟期": (110, 130)
        }
    
    def get_weather_data(self, start_date: str, end_date: str):
        """NASA POWER APIから気象データを取得"""
        parameters = [
            "T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", 
            "RH2M", "ALLSKY_SFC_SW_DWN", "WS2M"
        ]
        
        params = {
            "parameters": ",".join(parameters),
            "community": "AG",
            "longitude": self.longitude,
            "latitude": self.latitude,
            "start": start_date,
            "end": end_date,
            "format": "JSON"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"エラー: {str(e)}")
            return None
    
    def get_current_stage(self, days_since_planting: int) -> str:
        """現在の成長ステージを取得"""
        for stage_name, (start, end) in self.growth_stages.items():
            if start <= days_since_planting < end:
                return stage_name
        return "収穫後"
    
    def analyze_data(self, weather_data, planting_date):
        """気象データを分析"""
        if not weather_data or "properties" not in weather_data:
            return None
        
        params = weather_data["properties"]["parameter"]
        dates = sorted(params["T2M"].keys())
        
        df_data = {
            "日付": [],
            "平均気温": [],
            "最高気温": [],
            "最低気温": [],
            "降水量": [],
            "相対湿度": [],
            "日射量": [],
            "風速": [],
            "成長ステージ": [],
            "栽培日数": []
        }
        
        for date in dates:
            dt = datetime.strptime(date, "%Y%m%d")
            days_since_planting = (dt - planting_date).days
            stage = self.get_current_stage(days_since_planting)
            
            df_data["日付"].append(dt)
            df_data["平均気温"].append(params["T2M"].get(date))
            df_data["最高気温"].append(params["T2M_MAX"].get(date))
            df_data["最低気温"].append(params["T2M_MIN"].get(date))
            df_data["降水量"].append(params["PRECTOTCORR"].get(date))
            df_data["相対湿度"].append(params["RH2M"].get(date))
            df_data["日射量"].append(params["ALLSKY_SFC_SW_DWN"].get(date))
            df_data["風速"].append(params["WS2M"].get(date))
            df_data["成長ステージ"].append(stage)
            df_data["栽培日数"].append(days_since_planting)
        
        return pd.DataFrame(df_data)
    
    def get_recommendations(self, df: pd.DataFrame) -> list:
        """栽培推奨事項を生成"""
        recommendations = []
        
        if df is None or len(df) == 0:
            return ["データが不足しています"]
        
        # 直近7日間のデータ
        recent = df.tail(7)
        
        avg_temp = recent["平均気温"].mean()
        total_rain = recent["降水量"].sum()
        avg_humidity = recent["相対湿度"].mean()
        current_stage = df.iloc[-1]["成長ステージ"]
        
        # 温度評価
        if avg_temp < 10:
            recommendations.append({
                "type": "warning",
                "icon": "⚠️",
                "title": "低温警告",
                "message": "気温が低すぎます（平均{:.1f}°C）。霜害に注意し、保温対策を検討してください。".format(avg_temp)
            })
        elif avg_temp > 25:
            recommendations.append({
                "type": "warning",
                "icon": "⚠️",
                "title": "高温警告",
                "message": "気温が高めです（平均{:.1f}°C）。蒸散が激しくなるため、灌漑を増やしてください。".format(avg_temp)
            })
        else:
            recommendations.append({
                "type": "success",
                "icon": "✅",
                "title": "気温良好",
                "message": "気温は適正範囲内です（平均{:.1f}°C）".format(avg_temp)
            })
        
        # 降水量評価
        if total_rain < 15:
            recommendations.append({
                "type": "warning",
                "icon": "💧",
                "title": "水分不足",
                "message": "降水量が少ないです（{:.1f}mm）。灌漑が必要です。".format(total_rain)
            })
        elif total_rain > 50:
            recommendations.append({
                "type": "warning",
                "icon": "☔",
                "title": "過湿注意",
                "message": "降水量が多いです（{:.1f}mm）。過湿による病害に注意してください。".format(total_rain)
            })
        else:
            recommendations.append({
                "type": "success",
                "icon": "✅",
                "title": "水分適正",
                "message": "降水量は適正です（{:.1f}mm）".format(total_rain)
            })
        
        # 湿度評価
        if avg_humidity > 85:
            recommendations.append({
                "type": "danger",
                "icon": "🦠",
                "title": "病害リスク",
                "message": "湿度が高いです（{:.1f}%）。疫病のリスクが高まります。予防的な殺菌剤散布を検討してください。".format(avg_humidity)
            })
        
        # ステージ別アドバイス
        stage_advice = {
            "発芽期": "土壌を適度に湿らせ、10-15°Cを保ってください",
            "栄養成長期": "窒素肥料を施用し、土寄せを行ってください",
            "塊茎形成期": "水分管理が重要です。一定の土壌水分を維持してください",
            "塊茎肥大期": "カリウム肥料を追加し、十分な水分を供給してください",
            "成熟期": "灌漑を減らし、収穫の準備をしてください"
        }
        
        if current_stage in stage_advice:
            recommendations.append({
                "type": "info",
                "icon": "📋",
                "title": f"ステージ別アドバイス（{current_stage}）",
                "message": stage_advice[current_stage]
            })
        
        return recommendations


def create_weather_charts(df: pd.DataFrame):
    """気象データのグラフを作成"""
    
    # 4つのサブプロットを作成
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('気温トレンド', '降水量', '相対湿度', '日射量'),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # 1. 気温グラフ
    fig.add_trace(
        go.Scatter(x=df["日付"], y=df["平均気温"], name="平均気温",
                   line=dict(color='blue', width=2), mode='lines+markers'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df["日付"], y=df["最高気温"], name="最高気温",
                   line=dict(color='red', width=1, dash='dash')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df["日付"], y=df["最低気温"], name="最低気温",
                   line=dict(color='cyan', width=1, dash='dash')),
        row=1, col=1
    )
    # 最適温度範囲
    fig.add_hline(y=10, line_dash="dot", line_color="orange", row=1, col=1)
    fig.add_hline(y=25, line_dash="dot", line_color="red", row=1, col=1)
    
    # 2. 降水量
    fig.add_trace(
        go.Bar(x=df["日付"], y=df["降水量"], name="降水量",
               marker_color='lightblue'),
        row=1, col=2
    )
    
    # 3. 相対湿度
    fig.add_trace(
        go.Scatter(x=df["日付"], y=df["相対湿度"], name="相対湿度",
                   line=dict(color='green', width=2), mode='lines+markers',
                   fill='tozeroy', fillcolor='rgba(0,255,0,0.1)'),
        row=2, col=1
    )
    fig.add_hline(y=85, line_dash="dot", line_color="red", row=2, col=1)
    
    # 4. 日射量
    fig.add_trace(
        go.Scatter(x=df["日付"], y=df["日射量"], name="日射量",
                   line=dict(color='orange', width=2), mode='lines+markers',
                   fill='tozeroy', fillcolor='rgba(255,165,0,0.1)'),
        row=2, col=2
    )
    
    # レイアウト設定
    fig.update_xaxes(title_text="日付", row=2, col=1)
    fig.update_xaxes(title_text="日付", row=2, col=2)
    fig.update_yaxes(title_text="温度 (°C)", row=1, col=1)
    fig.update_yaxes(title_text="降水量 (mm)", row=1, col=2)
    fig.update_yaxes(title_text="湿度 (%)", row=2, col=1)
    fig.update_yaxes(title_text="日射量 (MJ/m²/day)", row=2, col=2)
    
    fig.update_layout(
        height=700,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    
    return fig


def main():
    """メインアプリケーション"""
    
    # ヘッダー
    st.title("🥔 じゃがいも農業管理システム")
    st.markdown("### NASA衛星データによる栽培管理ダッシュボード")
    st.markdown("---")
    
    # サイドバー設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # APIキー
        api_key = st.text_input(
            "NASA API キー",
            value="maAkjKjg0O2NrdgnryrGSruQNuZtMGkg8q2vCFxi",
            type="password",
            help="NASA POWER APIのキーを入力してください"
        )
        
        st.markdown("---")
        
        # 農場の位置
        st.subheader("📍 農場の位置")
        latitude = st.number_input(
            "緯度",
            min_value=-90.0,
            max_value=90.0,
            value=43.06,
            step=0.01,
            format="%.2f",
            help="農場の緯度を入力してください"
        )
        
        longitude = st.number_input(
            "経度",
            min_value=-180.0,
            max_value=180.0,
            value=141.35,
            step=0.01,
            format="%.2f",
            help="農場の経度を入力してください"
        )
        
        st.markdown("---")
        
        # 植え付け日
        st.subheader("📅 栽培情報")
        planting_date = st.date_input(
            "植え付け日",
            value=datetime(2025, 4, 15),
            min_value=datetime(2020, 1, 1),
            max_value=datetime.now()
        )
        
        # データ取得期間
        days_range = st.slider(
            "データ取得日数",
            min_value=30,
            max_value=180,
            value=130,
            step=10,
            help="植え付けからの日数"
        )
        
        st.markdown("---")
        
        # データ取得ボタン
        fetch_button = st.button("🌐 データ取得", type="primary", use_container_width=True)
    
    # 地図表示
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🗺️ 農場の位置")
        map_data = pd.DataFrame({'lat': [latitude], 'lon': [longitude]})
        st.map(map_data, zoom=10)
    
    with col2:
        st.subheader("📊 栽培情報")
        planting_datetime = datetime.combine(planting_date, datetime.min.time())
        days_since_planting = (datetime.now() - planting_datetime).days
        
        st.metric("植え付けからの日数", f"{days_since_planting} 日")
        
        farm_manager = PotatoFarmManagerUI(api_key, latitude, longitude)
        current_stage = farm_manager.get_current_stage(days_since_planting)
        
        # 成長ステージの表示
        stage_colors = {
            "発芽期": "🌱",
            "栄養成長期": "🌿",
            "塊茎形成期": "🥔",
            "塊茎肥大期": "🥔🥔",
            "成熟期": "✨",
            "収穫後": "📦"
        }
        
        st.markdown(f"""
        <div class="stage-box">
            <h3>{stage_colors.get(current_stage, '📌')} {current_stage}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # データ取得と表示
    if fetch_button:
        with st.spinner('NASA APIからデータを取得中...'):
            # 日付の計算
            start_date = planting_datetime.strftime("%Y%m%d")
            end_date = (planting_datetime + timedelta(days=days_range)).strftime("%Y%m%d")
            
            # データ取得
            weather_data = farm_manager.get_weather_data(start_date, end_date)
            
            if weather_data:
                st.success('✅ データ取得成功！')
                
                # データ分析
                df = farm_manager.analyze_data(weather_data, planting_datetime)
                
                if df is not None and len(df) > 0:
                    # セッションステートに保存
                    st.session_state['df'] = df
                    st.session_state['farm_manager'] = farm_manager
                    st.session_state['data_loaded'] = True
                else:
                    st.error('データの分析に失敗しました')
            else:
                st.error('データの取得に失敗しました')
    
    # データが読み込まれている場合
    if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
        df = st.session_state['df']
        farm_manager = st.session_state['farm_manager']
        
        # 推奨事項の表示
        st.subheader("💡 栽培推奨事項")
        recommendations = farm_manager.get_recommendations(df)
        
        cols = st.columns(2)
        for i, rec in enumerate(recommendations):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="recommendation-box">
                    <h4>{rec['icon']} {rec['title']}</h4>
                    <p>{rec['message']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 統計情報
        st.subheader("📈 統計情報")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_temp = df["平均気温"].mean()
            st.metric("平均気温", f"{avg_temp:.1f}°C", 
                     delta=f"{df['平均気温'].iloc[-1] - avg_temp:.1f}°C")
        
        with col2:
            total_rain = df["降水量"].sum()
            st.metric("総降水量", f"{total_rain:.1f}mm")
        
        with col3:
            avg_humidity = df["相対湿度"].mean()
            st.metric("平均湿度", f"{avg_humidity:.1f}%")
        
        with col4:
            avg_radiation = df["日射量"].mean()
            st.metric("平均日射量", f"{avg_radiation:.1f} MJ/m²")
        
        st.markdown("---")
        
        # グラフ表示
        st.subheader("📊 気象データの推移")
        fig = create_weather_charts(df)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # データテーブル
        with st.expander("📋 詳細データを表示"):
            st.dataframe(
                df[["日付", "平均気温", "最高気温", "最低気温", "降水量", 
                    "相対湿度", "日射量", "成長ステージ"]].tail(30),
                use_container_width=True
            )
        
        # CSVダウンロード
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSVダウンロード",
            data=csv,
            file_name=f"potato_farming_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        # 初回表示
        st.info("👈 サイドバーで設定を行い、「データ取得」ボタンをクリックしてください")
        
        # デモ画像やプレースホルダー
        st.markdown("""
        ### 🌟 機能
        
        - **リアルタイム気象データ**: NASA衛星データによる正確な気象情報
        - **成長ステージ管理**: じゃがいもの5つの成長段階を自動追跡
        - **栽培推奨**: 気象条件に基づいた灌漑・施肥のアドバイス
        - **インタラクティブグラフ**: 気温、降水量、湿度、日射量の可視化
        - **データエクスポート**: CSV形式でデータをダウンロード
        
        ### 📖 使い方
        
        1. サイドバーで農場の緯度・経度を入力
        2. 植え付け日を選択
        3. 「データ取得」ボタンをクリック
        4. グラフと推奨事項を確認
        """)


if __name__ == "__main__":
    main()
