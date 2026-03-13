import random


def sis_step(G, state, infection_prob, recovery_prob, blocked_nodes=None):
    """
    执行一轮 SIS 谣言传播

    SIS 模型：
    S -> I -> S
    节点恢复后会重新回到易感染状态
    """

    if blocked_nodes is None:
        blocked_nodes = set()

    new_state = state.copy()

    for node in G.nodes():
        if state[node] == "I":
            # 被限制的关键节点不能传播
            if node not in blocked_nodes:
                for neighbor in G.neighbors(node):
                    if state[neighbor] == "S":
                        if random.random() < infection_prob:
                            new_state[neighbor] = "I"

            # 恢复后回到 S，而不是 R
            if random.random() < recovery_prob:
                new_state[node] = "S"

    return new_state