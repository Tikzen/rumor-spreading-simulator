import random


def sir_step(G, state, infection_prob, recovery_prob, blocked_nodes=None):
    """
    执行一轮 SIR 谣言传播

    参数:
    G : networkx Graph
        社交网络图
    state : dict
        节点状态字典 {node: "S"/"I"/"R"}
    infection_prob : float
        传播概率
    recovery_prob : float
        恢复概率
    blocked_nodes : set
        被限制传播的关键节点集合
    """
    if blocked_nodes is None:
        blocked_nodes = set()

    new_state = state.copy()

    for node in G.nodes():
        if state[node] == "I":
            # 如果当前节点属于被限制传播的关键节点，则不能感染别人
            if node not in blocked_nodes:
                for neighbor in G.neighbors(node):
                    if state[neighbor] == "S":
                        if random.random() < infection_prob:
                            new_state[neighbor] = "I"

            # 当前节点仍然可以自然停止传播
            if random.random() < recovery_prob:
                new_state[node] = "R"

    return new_state