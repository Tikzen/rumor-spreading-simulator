import matplotlib.pyplot as plt
import networkx as nx


def draw_network_state(G, state, title="Network State"):
    """
    根据节点状态绘制网络图

    参数:
    G : networkx Graph
        社交网络图
    state : dict
        节点状态字典 {node: "S"/"I"/"R"}
    title : str
        图标题
    """

    color_map = []

    for node in G.nodes():
        if state[node] == "S":
            color_map.append("gray")
        elif state[node] == "I":
            color_map.append("red")
        else:
            color_map.append("blue")

    plt.figure(figsize=(8, 6))
    nx.draw(G, node_color=color_map, node_size=50)
    plt.title(title)
    plt.show()