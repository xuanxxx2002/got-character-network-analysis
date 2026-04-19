import networkx as nx
import pandas as pd
from cdlib import algorithms, evaluation, viz
import matplotlib.pyplot as plt

# 1. 載入 Game of Thrones 互動資料集
url = "https://raw.githubusercontent.com/mathbeveridge/asoiaf/master/data/asoiaf-book1-edges.csv"
edges = pd.read_csv(url)

# 修正：欄位名稱應為 'weight' (小寫)
G_got = nx.from_pandas_edgelist(edges, source='Source', target='Target', edge_attr='weight')

print(f"節點數量: {G_got.number_of_nodes()}")
print(f"邊數量: {G_got.number_of_edges()}")
# 2. 跑 Leiden 演算法進行社群偵測
coms_got = algorithms.leiden(G_got)

print(f"Leiden 演算法找到了 {len(coms_got.communities)} 個社群")
import matplotlib.patches as mpatches

# 1. 檢查代表性角色所在社群
key_characters = {
    "Eddard-Stark": "Stark",
    "Tywin-Lannister": "Lannister",
    "Daenerys-Targaryen": "Targaryen"
}

for name, house in key_characters.items():
    if name in G_got.nodes():
        community_id = [i for i, comm in enumerate(coms_got.communities) if name in comm][0]
        print(f"角色 {name} ({house}) 被歸類在社群 #{community_id}")

# 2. 印出每個社群的成員
for i, comm in enumerate(coms_got.communities):
    members = sorted(comm)
    print(f"\n社群 #{i}（{len(members)} 人）:")
    print(f"  成員: {members}")

# 3. 繪製網路圖並加上圖例
plt.figure(figsize=(12, 12))
viz.plot_network_clusters(G_got, coms_got, node_size=100)

# 建立圖例
colors = plt.cm.tab10.colors
legend_patches = [
    mpatches.Patch(color=colors[i % len(colors)], label=f'community #{i}')
    for i in range(len(coms_got.communities))
]
plt.legend(handles=legend_patches, loc='upper left', fontsize=8)
plt.title("Game of Thrones - Leiden Community Detection")
plt.show()
# 5. 計算模組度 (Modularity)
mod_got = evaluation.newman_girvan_modularity(G_got, coms_got)
print(f"Game of Thrones 網路的模組度 Q: {mod_got.score:.4f}")

if mod_got.score > 0.3:
    print("結果分析：模組度超過 0.3，顯示該網路具有明顯的社群結構（家族/勢力範圍）。")
else:
    print("結果分析：模組度較低，角色間的互動可能跨度較大，界線不夠明顯。")
