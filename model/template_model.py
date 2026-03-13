"""
传播模型模板

复制此文件并修改即可创建新的传播模型
"""

import random

# 模型名称
MODEL_NAME = "TemplateModel"

# 节点状态
STATES = ["S", "I", "R"]


def step(G, state, infection_prob, recovery_prob, blocked_nodes=None):
    """
    执行一轮传播
    """

    if blocked_nodes is None:
        blocked_nodes = set()

    new_state = state.copy()

    for node in G.nodes():

        if state[node] == "I":

            # 感染邻居
            for neighbor in G.neighbors(node):

                if state[neighbor] == "S":
                    if random.random() < infection_prob:
                        new_state[neighbor] = "I"

            # 恢复
            if random.random() < recovery_prob:
                new_state[node] = "R"

    return new_state