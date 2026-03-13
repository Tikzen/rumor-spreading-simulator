import random


def si_step(G, state, infection_prob, recovery_prob=0, blocked_nodes=None):
    """
    执行一轮 SI 谣言传播

    SI 模型：
    S -> I
    一旦成为传播者，就不会退出传播状态
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

    return new_state