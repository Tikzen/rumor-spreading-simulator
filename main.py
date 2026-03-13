from network.generator import create_network
from model.sir_model import sir_step
from visualization.network_anim import animate_network
import matplotlib.pyplot as plt
import random

# 固定随机种子，保证每次运行结果一致
random.seed(42)

# ===== 1. 创建网络 =====
G = create_network(100, 3)

# ===== 2. 初始化节点状态 =====
state = {node: "S" for node in G.nodes()}

# 随机选择一个初始传播者
initial_node = random.choice(list(G.nodes()))
state[initial_node] = "I"

# ===== 3. 设置传播参数 =====
infection_prob = 0.3
recovery_prob = 0.1
rounds = 20

# ===== 4. 数据记录 =====
S_counts = []
I_counts = []
R_counts = []
history = []

# 记录初始状态（第0轮）
history.append(state.copy())

# ===== 5. 传播循环 =====
for step in range(rounds):
    # 执行一轮 SIR 传播
    state = sir_step(G, state, infection_prob, recovery_prob)

    # 记录当前轮状态
    history.append(state.copy())

    # 统计 S / I / R 数量
    S_count = sum(1 for s in state.values() if s == "S")
    I_count = sum(1 for s in state.values() if s == "I")
    R_count = sum(1 for s in state.values() if s == "R")

    S_counts.append(S_count)
    I_counts.append(I_count)
    R_counts.append(R_count)

    print(f"第{step + 1}轮: S={S_count}, I={I_count}, R={R_count}")

    # 如果没有传播者了，提前结束
    if I_count == 0:
        print("传播结束")
        break

# ===== 6. 传播峰值统计 =====
peak_I = max(I_counts)
peak_round = I_counts.index(peak_I) + 1

print("\n传播峰值：")
print(f"第{peak_round}轮达到最大传播人数: {peak_I}")

# ===== 7. 绘制 SIR 曲线 =====
actual_rounds = len(S_counts)

plt.figure(figsize=(8, 6))
plt.plot(range(1, actual_rounds + 1), S_counts, label="Susceptible (S)")
plt.plot(range(1, actual_rounds + 1), I_counts, label="Infected (I)")
plt.plot(range(1, actual_rounds + 1), R_counts, label="Recovered (R)")

plt.title("SIR Rumor Propagation")
plt.xlabel("Round")
plt.ylabel("Number of Nodes")
plt.legend()
plt.grid(True)
plt.show(block=False)

# ===== 8. 播放网络传播动画 =====
ani = animate_network(G, history)
plt.show()