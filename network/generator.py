import networkx as nx


def create_network(n, m):
    """
    创建Barabási-Albert无标度网络

    参数:
    n : 节点数量
    m : 每个新节点连接的边数
    """

    G = nx.barabasi_albert_graph(n, m)
    return G