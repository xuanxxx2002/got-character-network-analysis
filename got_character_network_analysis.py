import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
from cdlib import algorithms, evaluation

# ── 資料載入 ───────────────────────────────────────────────
url   = "https://raw.githubusercontent.com/mathbeveridge/asoiaf/master/data/asoiaf-book1-edges.csv"
edges = pd.read_csv(url)
G     = nx.from_pandas_edgelist(edges, source="Source", target="Target", edge_attr="weight")

print(f"節點數: {G.number_of_nodes()}  邊數: {G.number_of_edges()}\n")

# ── 中心性分析 ─────────────────────────────────────────────
centrality = pd.DataFrame({
    "degree":      nx.degree_centrality(G),
    "betweenness": nx.betweenness_centrality(G, weight="weight"),
    "closeness":   nx.closeness_centrality(G),
    "pagerank":    nx.pagerank(G, weight="weight"),
}).sort_values("pagerank", ascending=False)
centrality.index.name = "character"
centrality.to_csv("centrality_results.csv")

print("=== Top-10 影響力角色（PageRank）===")
print(centrality.head(10).to_string())

# ── 社群偵測（三種演算法比較）─────────────────────────────
algo_results = {
    "Leiden":           algorithms.leiden(G),
    "Louvain":          algorithms.louvain(G),
    "Label Propagation": algorithms.label_propagation(G),
}

print("\n=== 演算法比較 ===")
rows = []
for name, coms in algo_results.items():
    mod  = evaluation.newman_girvan_modularity(G, coms).score
    cond = evaluation.conductance(G, coms).score
    print(f"[{name}]  社群數: {len(coms.communities)}  模組度 Q: {mod:.4f}  導出率: {cond:.4f}")
    rows.append({"algorithm": name, "communities": len(coms.communities),
                 "modularity": mod, "conductance": cond})

algo_df = pd.DataFrame(rows).set_index("algorithm")
algo_df.to_csv("algorithm_comparison.csv")

best_name = algo_df["modularity"].idxmax()
best_coms = algo_results[best_name]
print(f"\n最佳演算法：{best_name}\n")

# ── 社群成員輸出 ───────────────────────────────────────────
community_map = {}
for cid, members in enumerate(best_coms.communities):
    for node in members:
        community_map[node] = cid

community_df = pd.DataFrame({
    "character":  list(community_map.keys()),
    "community":  list(community_map.values()),
}).set_index("character")
community_df = community_df.join(centrality)
community_df.to_csv("community_membership.csv")

# ── 代表性角色所在社群 ────────────────────────────────────
key_characters = {
    "Eddard-Stark": "Stark",
    "Tywin-Lannister": "Lannister",
    "Daenerys-Targaryen": "Targaryen",
    "Jon-Snow": "Stark/Night's Watch",
    "Cersei-Lannister": "Lannister",
}
print("=== 代表性角色社群 ===")
for name, house in key_characters.items():
    if name in community_map:
        cid = community_map[name]
        pr  = centrality.loc[name, "pagerank"] if name in centrality.index else 0
        print(f"  {name} ({house})  → 社群 #{cid}  PageRank: {pr:.4f}")

# ── 視覺化 ─────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# 左上：社群著色網路圖（Spring Layout，標注 Top-20 角色）
top20    = set(centrality.head(20).index)
pos      = nx.spring_layout(G, seed=42, k=0.4)
n_com    = len(best_coms.communities)
cmap     = cm.get_cmap("tab20", n_com)
colors   = [cmap(community_map.get(n, 0)) for n in G.nodes()]
sizes    = [centrality.loc[n, "pagerank"] * 8000 if n in centrality.index else 50 for n in G.nodes()]

nx.draw_networkx_edges(G, pos, ax=axes[0, 0], alpha=0.15, edge_color="#aaaaaa", width=0.5)
nx.draw_networkx_nodes(G, pos, ax=axes[0, 0], node_color=colors, node_size=sizes, alpha=0.9)
labels_top = {n: n.replace("-", "\n") for n in G.nodes() if n in top20}
nx.draw_networkx_labels(G, pos, labels=labels_top, ax=axes[0, 0], font_size=6)

legend_patches = [mpatches.Patch(color=cmap(i), label=f"Community #{i}")
                  for i in range(min(n_com, 10))]
axes[0, 0].legend(handles=legend_patches, loc="upper left", fontsize=7, ncol=2)
axes[0, 0].set_title(f"GoT Character Network — {best_name}\n(node size = PageRank)")
axes[0, 0].axis("off")

# 右上：Top-15 角色四項指標長條圖
top15 = centrality.head(15)
x     = range(len(top15))
w     = 0.2
axes[0, 1].bar([i - 1.5*w for i in x], top15["pagerank"],    w, label="PageRank",    color="#4C72B0")
axes[0, 1].bar([i - 0.5*w for i in x], top15["betweenness"], w, label="Betweenness", color="#DD8452")
axes[0, 1].bar([i + 0.5*w for i in x], top15["closeness"],   w, label="Closeness",   color="#55A868")
axes[0, 1].bar([i + 1.5*w for i in x], top15["degree"],      w, label="Degree",      color="#C44E52")
axes[0, 1].set_xticks(list(x))
axes[0, 1].set_xticklabels([n.replace("-", "\n") for n in top15.index], fontsize=7)
axes[0, 1].set_title("Top-15 Characters — Centrality Metrics")
axes[0, 1].set_ylabel("Score")
axes[0, 1].legend(fontsize=8)

# 左下：演算法模組度比較
colors_bar = ["steelblue", "tomato", "seagreen"]
axes[1, 0].bar(algo_df.index, algo_df["modularity"], color=colors_bar, alpha=0.85)
axes[1, 0].axhline(0.3, color="gray", linestyle="--", linewidth=1, label="Q = 0.3 threshold")
for i, (idx, row) in enumerate(algo_df.iterrows()):
    axes[1, 0].text(i, row["modularity"] + 0.005, f'{row["modularity"]:.3f}', ha="center", fontsize=9)
axes[1, 0].set_title("Algorithm Comparison — Modularity Q")
axes[1, 0].set_ylabel("Modularity Q")
axes[1, 0].legend(fontsize=8)

# 右下：各社群規模 + Top 角色
com_sizes = [(cid, len(members)) for cid, members in enumerate(best_coms.communities)]
com_sizes.sort(key=lambda x: -x[1])
cids  = [f"#{c}" for c, _ in com_sizes]
sizes_bar = [s for _, s in com_sizes]
bar_colors = [cmap(c) for c, _ in com_sizes]
axes[1, 1].bar(cids, sizes_bar, color=bar_colors, alpha=0.85)
axes[1, 1].set_title(f"Community Size Distribution ({best_name})")
axes[1, 1].set_xlabel("Community")
axes[1, 1].set_ylabel("Number of Characters")
for i, (cid, size) in enumerate(com_sizes):
    top_char = community_df[community_df["community"] == cid]["pagerank"].idxmax()
    axes[1, 1].text(i, size + 0.3, top_char.split("-")[0], ha="center", fontsize=7, rotation=45)

plt.suptitle("Game of Thrones — Character Network Analysis (Book 1)", fontsize=14, y=1.01)
plt.tight_layout()
plt.savefig("got_network_analysis.png", dpi=150, bbox_inches="tight")
plt.show()
print("\n已儲存：centrality_results.csv、community_membership.csv、algorithm_comparison.csv、got_network_analysis.png")
