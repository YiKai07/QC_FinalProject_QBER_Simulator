import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import platform

# --- 字體設定 ---
system = platform.system()
if system == 'Windows':
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  
elif system == 'Darwin':
    plt.rcParams['font.sans-serif'] = ['PingFang TC', 'Arial Unicode MS']  
else:
    plt.rcParams['font.sans-serif'] = ['Noto Sans CJK TC', 'WenQuanYi Micro Hei']  
plt.rcParams['axes.unicode_minus'] = False

# 頁面基本設定
st.set_page_config(page_title="QEYSSat 光害與 QBER 模擬工具", layout="wide")

st.title("量子通訊光害與大氣傳輸 QBER 模擬工具")

# 側邊欄：情境與參數設定
st.sidebar.header("系統情境與參數設定")

# 1. 鏈路情境選擇
link_scenario = st.sidebar.radio("選擇通訊情境 (Scenario)", ["上行鏈路 (Uplink) - 地面發送/衛星接收", "下行鏈路 (Downlink) - 衛星發送/地面接收"])

st.sidebar.markdown("---")
st.sidebar.subheader("快速套用論文典型站點參數")

# 初始化 Session State，確保滑桿有預設值可連動
if 'radiance' not in st.session_state:
    st.session_state.radiance = 50.0
if 'signal_rate' not in st.session_state:
    st.session_state.signal_rate = 2000
if 'altitude' not in st.session_state:
    st.session_state.altitude = 45.0

# 修正按鈕觸發邏輯：點擊時直接修改 st.session_state 數值
if st.sidebar.button("滑鐵盧大學 (QGS-UW)"):
    st.session_state.radiance = 53.5 if "Uplink" in link_scenario else 45.0
    st.session_state.signal_rate = 1500
    st.session_state.altitude = 45.0

if st.sidebar.button("暗空觀測台 (QGS-RAO)"):
    st.session_state.radiance = 3.4
    st.session_state.signal_rate = 2000
    st.session_state.altitude = 15.0

st.sidebar.markdown("---")

# 將滑桿的值直接與 session_state 綁定 (使用 value=st.session_state.[key])
# 並透過指定 key 讓 Streamlit 自動處理雙向連動
altitude = st.sidebar.slider("當前衛星仰角 θ (度)", min_value=10.0, max_value=90.0, key="altitude", step=1.0)
radiance = st.sidebar.slider("地表光害輻射率 (nW/cm²/sr)", min_value=0.0, max_value=120.0, key="radiance", step=0.1)
signal_rate = st.sidebar.slider("預期訊號光子率 (Hz)", min_value=100, max_value=10000, key="signal_rate", step=100)

st.sidebar.markdown("---")
st.sidebar.markdown("**論文參考指標：**")
st.sidebar.markdown("* **QGS-RAO (鄉村暗空)**：輻射率約 **3.4 nW/cm²/sr** (極低雜訊)")
st.sidebar.markdown("* **QGS-UW (城市近郊)**：輻射率約 **37.7 ~ 53.5 nW/cm²/sr**")
st.sidebar.markdown("* **QGS-UC (卡加利校園)**：輻射率約 **105.3 nW/cm²/sr** (高度光害)")

# --- 核心物理模型計算 ---
theta_rad = np.radians(altitude)
csc_theta = 1.0 / np.sin(theta_rad)

# 1. 大氣透射率模型 e_atm = 10^(-0.32 * csc(θ))
e_atm = 10 ** (-0.32 * csc_theta)

# 2. 背景雜訊估算 (根據上下行鏈路特性調整物理縮放因子)
if "Uplink" in link_scenario:
    C_scale = 38.0  
    background_noise = radiance * C_scale * e_atm * csc_theta
else:
    C_scale = 8.0  
    background_noise = radiance * C_scale * e_atm

# 3. 量子誤碼率 (QBER) 計算模型
base_error = 1.0
qber = (background_noise / (2 * signal_rate + background_noise)) * 100.0 + base_error

# 顯示即時指標
col1, col2, col3 = st.columns(3)
col1.metric(label="當前大氣透射率 (e_atm)", value=f"{e_atm:.4f}")
col2.metric(label="預估背景雜訊率 (Photon Noise Rate)", value=f"{background_noise:.1f} Hz")

# 動態調整 QBER 顯示顏色警示
if qber > 12.62:
    col3.metric(label="預測量子誤碼率 (QBER)", value=f"{qber:.2f}%", delta="全面斷線 (破安全上限)", delta_color="inverse")
elif qber > 5.0:
    col3.metric(label="預測量子誤碼率 (QBER)", value=f"{qber:.2f}%", delta="BB84 實務高風險", delta_color="off")
else:
    col3.metric(label="預測量子誤碼率 (QBER)", value=f"{qber:.2f}%", delta="安全連線中", delta_color="normal")

# st.markdown("---")
st.subheader(f"動態分析：在當前光害 ({radiance} nW/cm²/sr) 下，仰角對 QBER 的影響趨勢")

# --- 產生全仰角角度趨勢圖數據 ---
angles = np.linspace(10, 90, 161)
angles_rad = np.radians(angles)
csc_angles = 1.0 / np.sin(angles_rad)
e_atm_array = 10 ** (-0.32 * csc_angles)

if "Uplink" in link_scenario:
    noise_array = radiance * C_scale * e_atm_array * csc_angles
else:
    noise_array = radiance * C_scale * e_atm_array

qber_array = (noise_array / (2 * signal_rate + noise_array)) * 100.0 + base_error

# 找出連線黃金交叉仰角
safe_alt_5 = angles[qber_array < 5.0][0] if np.any(qber_array < 5.0) else None

# 繪製高品質科研對比圖表
fig, ax = plt.subplots(figsize=(9, 3.5))
ax.plot(angles, qber_array, color='#0f172a', linewidth=3, label=f"模擬鏈路 QBER 曲線")

# 繪製安全邊界與理論上限
ax.axhline(y=5.0, color='#10b981', linestyle='--', linewidth=1.5, label="QEYSSat 實務安全極限 (5.0%)")
ax.axhline(y=11.0, color='#f59e0b', linestyle='-.', linewidth=1.5, label="傳統 BB84 Shor-Preskill 安全上限 (11.0%)")
ax.axhline(y=12.62, color='#ef4444', linestyle=':', linewidth=1.5, label="論文引入 RFI-QKD 安全上限 (12.62%)")

# 標註關鍵交叉點
if "Uplink" in link_scenario and radiance > 30:
    if safe_alt_5:
        ax.axvline(x=safe_alt_5, color='#10b981', linestyle=':', alpha=0.7)
        ax.text(safe_alt_5 + 1, 6, f"實務解鎖仰角: {safe_alt_5:.1f}°\n(符合城市 >40° 限制)", color='#065f46', fontsize=9)
else:
    if safe_alt_5 and safe_alt_5 <= 10.1:
        ax.text(12, base_error + 1, "鄉村暗空環境：\n地平線附近 (仰角10°) 即可安全連線", color='#065f46', fontsize=10)

ax.set_title(f"{link_scenario.split(' ')[0]} - 仰角 vs 量子誤碼率 (QBER) 關係圖", fontsize=14, pad=15)
ax.set_xlabel("衛星仰角 Altitude Angle (度 °)", fontsize=11)
ax.set_ylabel("量子誤碼率 QBER (%)", fontsize=11)
ax.set_xlim(10, 90)
ax.set_ylim(0, max(16, np.max(qber_array) + 2))
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc="upper right", frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0')

st.pyplot(fig)