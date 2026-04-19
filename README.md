# got-character-network-analysis

以《冰與火之歌》第一冊的角色互動資料為基礎，分析角色中心性、社群結構與勢力分佈。

## 分析流程

```
asoiaf-book1-edges.csv（GitHub）
          ↓
     NetworkX 圖形
          ↓
┌─────────────────────┬──────────────────────┐
中心性分析               社群偵測（三種演算法）
PageRank / Betweenness   Leiden / Louvain
Closeness / Degree       Label Propagation
          ↓                      ↓
     Top-15 角色排名         模組度比較 + 社群規模
```

## 輸出

| 檔案 | 內容 |
|---|---|
| `centrality_results.csv` | 所有角色的四項中心性指標 |
| `community_membership.csv` | 每位角色所屬社群 + 中心性數值 |
| `algorithm_comparison.csv` | 三種演算法的模組度與導出率比較 |
| `got_network_analysis.png` | 2×2 圖表（網路圖、指標長條圖、演算法比較、社群規模）|

## 視覺化說明

| 圖表 | 說明 |
|---|---|
| 社群著色網路圖 | 節點大小 = PageRank，顏色 = 社群，標注 Top-20 角色 |
| Centrality Metrics | Top-15 角色的四項指標並排比較 |
| Algorithm Comparison | 三種演算法的模組度 Q 對照 |
| Community Size | 各社群人數分佈，標注各社群最具影響力角色 |

## 快速開始

**安裝依賴**

```bash
python -m pip install networkx pandas matplotlib cdlib leidenalg
```

**執行**

```bash
python got_character_network_analysis.py
```

## 資料集

[asoiaf-book1-edges.csv](https://github.com/mathbeveridge/asoiaf) — 角色共同出現於同一段落即建立一條邊，邊的權重為共同出現次數。
