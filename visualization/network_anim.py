import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx


def animate_network(G, history):
    """
    根据 history 制作网络传播动画
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # 固定布局，避免每一帧节点乱跳
    pos = nx.spring_layout(G, seed=42)

    def update(frame):
        ax.clear()

        state = history[frame]
        color_map = []

        for node in G.nodes():
            if state[node] == "S":
                color_map.append("gray")
            elif state[node] == "I":
                color_map.append("red")
            else:
                color_map.append("blue")

        nx.draw(G, pos, node_color=color_map, node_size=50, ax=ax)
        ax.set_title(f"Rumor Propagation Simulation  |  Round {frame}")

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=len(history),
        interval=800,
        repeat=False
    )

    return ani