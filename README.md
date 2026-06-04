# QEYSSat 光害與大氣傳輸 QBER 模擬工具

本工具為**量子密碼學期末自主學習專題研究**之實作成果。程式依據加拿大 QEYSSat（Quantum Encryption and Science Satellite）任務之雙線鏈路物理模型設計，旨在模擬並定量評估地面站周圍之人造光害（Light Pollution）與不同衛星仰角（Altitude Angle）對量子誤碼率（QBER）的動態影響。

## 📌 功能特色

- **雙線鏈路情境切換**：支援「上行鏈路（Uplink）」與「下行鏈路（Downlink）」兩種不同的光學衰減與雜訊模型。
- **典型站點一鍵套用**：內建論文中真實觀測站點的參數，包含高光害城市近郊的**滑鐵盧大學 (QGS-UW)** 與環境極為乾淨的**鄉村暗空觀測台 (QGS-RAO)**。
- **科研級動態圖表**：即時繪製仰角與 QBER 的關係曲線，並自動標註傳統 BB84 協定（11.0%）與論文引入之 RFI-QKD 協定（12.62%）的理論安全上限，以及實務安全臨界線（5.0%）。
- **跨平台字體優化**：自動偵測 Windows、Mac (Darwin) 與 Linux 系統，動態載入相應的繁體中文字體，確保圖表標籤不漏字、不出現亂碼。

## 📐 核心物理模型

本模擬工具實作並整合了以下論文核心公式：

1. **大氣透射率模型 (Atmospheric Transmission)**：
   $$e_{atm} = 10^{-0.32 \csc(\theta)}$$
   其中 $\theta$ 為衛星仰角。仰角愈低，光子穿過大氣層的路徑愈長，損耗愈多。

2. **幾何足跡放大因子 (Footprint Expansion)**：
   在上行鏈路中，衛星接收器的可視地表面積（Footprint）會隨 $\csc(\theta)$ 的幾何投影項呈非線性放大，導致低仰角時接收到大量的地表反光雜訊。

3. **量子誤碼率 (QBER) 計算**：
   $$QBER = \frac{N_{background}}{2 \times N_{signal} + N_{background}} \times 100\% + \text{Base Error}$$
   藉此直接評估在特定背景雜訊率下，接收端接收到的有效單光子訊噪比。

## 💻 快速開始

### 1. 環境需求
請確保您的電腦已安裝 Python 3.8+ 及其它必要套件。

### 2. 安裝依賴套件
在終端機（Terminal）或命令提示字元（CMD）中執行以下指令安裝所需套件：

pip install streamlit numpy pandas matplotlib

### 3. 啟動模擬工具
將程式碼儲存為 `app.py`，並在該檔案所在的資料夾目錄下執行：

streamlit run app.py

程式啟動後，系統會自動在您的瀏覽器中開啟互動式網頁介面（預設網址為 http://localhost:8501 ）。

## 📊 模擬操作與口頭報告 Demo 指南

1. **上行鏈路城市瓶頸展示**：
   選擇「上行鏈路（Uplink）」，並點擊 **[滑鐵盧大學 (QGS-UW)]** 按鈕。此時預設的預期訊號光子率會設為 `7000 Hz` 以對抗城市光害。圖表上會清晰顯示：當衛星仰角**大於 $40^\circ \sim 45^\circ$** 時，QBER 曲線才會順利降至 5% 的實務安全極限以下，完美驗證論文結論。
   
2. **訊噪比（SNR）斷線演示**：
   在城市站點（QGS-UW）參數下，若將「預期訊號光子率」滑桿往左拉低（例如調至 `1500 Hz`），預測 QBER 將在全仰角區間衝破理論安全上限（11.0% 或 12.62%），畫面會即時發出「全面斷線」警示，這能強烈凸顯出**傳統 BB84 協定在光害環境下對高頻雷射光源（MHz 等級發射率）與鏈路損耗調校的嚴苛依賴性**。

3. **鄉村暗空優勢對比**：
   點擊 **[暗空觀測台 (QGS-RAO)]**，地表光害輻射率將降至極低的 `3.4 nW/cm²/sr`。此時可觀察到即使訊號光子率較低，衛星只要出現在地平線附近（**仰角 $10^\circ$**），便能立刻跨過安全門檻建立加密連線，擁有極長的有效通訊窗口。

## 📜 專題資訊

- **課程名稱**：量子密碼學
- **報告主題**：Estimating the impact of light pollution on quantum communication between QEYSSat and Canadian quantum ground station sites