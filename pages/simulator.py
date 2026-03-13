import sys
import os
import time
import random
import importlib
import pkgutil

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager
import networkx as nx

# 把项目根目录加入 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import model
from network.generator import create_network
from utils.exporter import build_export_zip


# =========================
# Matplotlib 中文显示修复
# =========================
def setup_matplotlib_font():
    """
    修复 matplotlib 中文显示问题：
    1. 优先加载项目内置字体文件
    2. 若项目字体不存在，再回退系统中文字体
    3. 最后才使用 DejaVu Sans
    """
    current_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(current_dir)

    font_candidates = [
        os.path.join(project_root, "assets", "fonts", "NotoSansSC-Regular.ttf"),
        os.path.join(project_root, "assets", "fonts", "NotoSansCJKsc-Regular.otf"),
        os.path.join(project_root, "assets", "fonts", "SourceHanSansCN-Regular.otf"),
    ]

    # 1) 优先加载项目内字体文件
    for font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                font_manager.fontManager.addfont(font_path)
                font_prop = font_manager.FontProperties(fname=font_path)
                font_name = font_prop.get_name()

                mpl.rcParams["font.family"] = "sans-serif"
                mpl.rcParams["font.sans-serif"] = [font_name]
                mpl.rcParams["axes.unicode_minus"] = False

                return f"{font_name} (from file)"
            except Exception:
                pass

    # 2) 回退系统字体
    preferred_fonts = [
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
        "KaiTi",
        "FangSong",
        "Noto Sans CJK SC",
        "Noto Sans SC",
        "Source Han Sans SC",
        "Source Han Sans CN",
        "Arial Unicode MS",
        "WenQuanYi Zen Hei",
        "DejaVu Sans",
    ]

    available_fonts = {f.name for f in font_manager.fontManager.ttflist}

    for font_name in preferred_fonts:
        if font_name in available_fonts:
            mpl.rcParams["font.family"] = "sans-serif"
            mpl.rcParams["font.sans-serif"] = [font_name]
            mpl.rcParams["axes.unicode_minus"] = False
            return f"{font_name} (system)"

    # 3) 最终兜底
    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    mpl.rcParams["axes.unicode_minus"] = False
    return "DejaVu Sans (fallback)"


SELECTED_FONT = setup_matplotlib_font()


# =========================
# 模型加载
# =========================
def load_models():
    models = {}

    for _, module_name, _ in pkgutil.iter_modules(model.__path__):
        if module_name.startswith("__"):
            continue

        module = importlib.import_module(f"model.{module_name}")

        # 新规范模型
        if hasattr(module, "MODEL_NAME") and hasattr(module, "STATES") and hasattr(module, "step"):
            models[module.MODEL_NAME] = {
                "step": module.step,
                "states": module.STATES,
                "module_name": module_name,
            }
            continue

        # 兼容旧规范
        if module_name == "si_model" and hasattr(module, "si_step"):
            models["SI"] = {
                "step": module.si_step,
                "states": ["S", "I"],
                "module_name": module_name,
            }
        elif module_name == "sis_model" and hasattr(module, "sis_step"):
            models["SIS"] = {
                "step": module.sis_step,
                "states": ["S", "I"],
                "module_name": module_name,
            }
        elif module_name == "sir_model" and hasattr(module, "sir_step"):
            models["SIR"] = {
                "step": module.sir_step,
                "states": ["S", "I", "R"],
                "module_name": module_name,
            }

    return models


MODEL_REGISTRY = load_models()


# =========================
# 可视化辅助函数
# =========================
def get_state_color(state_value):
    color_map = {
        "S": "gray",
        "I": "red",
        "R": "blue",
        "E": "orange",
    }
    return color_map.get(state_value, "purple")


def draw_network_frame(G, state, pos, title="Network State", blocked_nodes=None):
    if blocked_nodes is None:
        blocked_nodes = set()

    node_colors = []
    node_sizes = []

    for node in G.nodes():
        node_colors.append(get_state_color(state[node]))
        node_sizes.append(120 if node in blocked_nodes else 50)

    fig, ax = plt.subplots(figsize=(6, 5))
    nx.draw(G, pos, node_color=node_colors, node_size=node_sizes, ax=ax)
    ax.set_title(title)
    return fig


def get_blocked_nodes(G, block_ratio):
    centrality = nx.degree_centrality(G)
    num_blocked = max(1, int(len(G.nodes()) * block_ratio))
    sorted_nodes = sorted(centrality, key=centrality.get, reverse=True)
    return set(sorted_nodes[:num_blocked])


# =========================
# 仿真辅助函数
# =========================
def choose_initial_node(G, blocked_nodes, source_type):
    """
    source_type 固定使用：
    - random
    - normal
    - key
    """
    all_nodes = list(G.nodes())

    # 用于“关键节点传播源”实验的高中心性节点
    source_key_nodes = list(get_blocked_nodes(G, 0.05))

    # 普通节点：避开高中心性节点和被限制传播节点
    normal_nodes = [
        node for node in all_nodes
        if node not in source_key_nodes and node not in blocked_nodes
    ]

    # 关键节点传播源优先选高中心性且未被阻断的节点
    available_key_nodes = [
        node for node in source_key_nodes
        if node not in blocked_nodes
    ]

    # 随机节点也尽量避免直接落在被限制传播节点上
    available_random_nodes = [
        node for node in all_nodes
        if node not in blocked_nodes
    ]

    if source_type == "key":
        candidate_nodes = available_key_nodes or source_key_nodes or available_random_nodes or all_nodes
    elif source_type == "normal":
        candidate_nodes = normal_nodes or available_random_nodes or all_nodes
    else:  # random
        candidate_nodes = available_random_nodes or all_nodes

    return random.choice(candidate_nodes)


def run_simulation(
    model_type,
    num_nodes,
    attach_edges,
    infection_prob,
    recovery_prob,
    rounds,
    seed,
    source_type,
    enable_refutation=False,
    refutation_round=10,
    refutation_factor=0.5,
    enable_key_control=False,
    key_control_ratio=0.05,
):
    random.seed(seed)

    G = create_network(num_nodes, attach_edges)

    blocked_nodes = set()
    if enable_key_control:
        blocked_nodes = get_blocked_nodes(G, key_control_ratio)

    # 后端兜底保护：若初始传播源类型为关键节点，则不对关键节点传播做限制
    if source_type == "key" and enable_key_control:
        enable_key_control = False
        blocked_nodes = set()

    model_info = MODEL_REGISTRY[model_type]
    step_func = model_info["step"]
    states_list = model_info["states"]

    state = {node: "S" for node in G.nodes()}

    initial_node = choose_initial_node(G, blocked_nodes, source_type)

    # 再次兜底：即使 initial_node 落在 blocked_nodes 中，也将其移出限制集合
    blocked_nodes.discard(initial_node)

    state[initial_node] = "I"

    history = [state.copy()]
    count_history = {s: [] for s in states_list}

    for step in range(rounds):
        current_infection_prob = (
            infection_prob * refutation_factor
            if enable_refutation and step + 1 >= refutation_round
            else infection_prob
        )

        state = step_func(
            G,
            state,
            current_infection_prob,
            recovery_prob,
            blocked_nodes=blocked_nodes
        )

        history.append(state.copy())

        counts = {s: 0 for s in states_list}
        for node_state in state.values():
            if node_state in counts:
                counts[node_state] += 1

        for s in states_list:
            count_history[s].append(counts[s])

        S_count = counts.get("S", 0)
        I_count = counts.get("I", 0)

        # 终止条件
        if model_type == "SI" and S_count == 0:
            break

        if model_type in ["SIS", "SIR"] and I_count == 0:
            break

    I_counts = count_history.get("I", [])
    peak_I = max(I_counts) if I_counts else 0
    peak_round = I_counts.index(peak_I) + 1 if I_counts else 0

    final_R = count_history.get("R", [0])[-1] if "R" in count_history and count_history["R"] else 0
    final_ratio = final_R / num_nodes if num_nodes > 0 else 0

    return {
        "G": G,
        "history": history,
        "count_history": count_history,
        "states_list": states_list,
        "peak_I": peak_I,
        "peak_round": peak_round,
        "final_R": final_R,
        "final_ratio": final_ratio,
        "blocked_nodes": blocked_nodes,
        "initial_node": initial_node,
    }


# =========================
# 页面配置
# =========================
st.set_page_config(
    page_title="谣言传播模拟器",
    layout="wide"
)

st.title("社交网络谣言传播与干预策略模拟平台")
st.markdown("**基于复杂网络与多传播模型的信息扩散仿真系统**")


# =========================
# Session State
# =========================
if "simulation_result" not in st.session_state:
    st.session_state.simulation_result = None

if "comparison_result" not in st.session_state:
    st.session_state.comparison_result = None

if "source_experiment_result" not in st.session_state:
    st.session_state.source_experiment_result = None


# =========================
# 侧边栏
# =========================
st.sidebar.header("参数设置")
st.sidebar.caption(f"当前图表字体：{SELECTED_FONT}")

available_models = list(MODEL_REGISTRY.keys())
default_model_index = available_models.index("SIR") if "SIR" in available_models else 0
model_type = st.sidebar.selectbox(
    "传播模型",
    available_models,
    index=default_model_index,
    key="model_type_select"
)

source_labels = {
    "random": "随机节点",
    "normal": "普通节点",
    "key": "关键节点",
}
source_keys = ["random", "normal", "key"]

source_type = st.sidebar.selectbox(
    "初始传播源类型",
    source_keys,
    format_func=lambda x: source_labels[x],
    key="source_type_select"
)

num_nodes = st.sidebar.slider("节点数量", 50, 300, 100, 10, key="num_nodes_slider")
attach_edges = st.sidebar.slider("每个新节点连接边数", 1, 10, 3, 1, key="attach_edges_slider")
infection_prob = st.sidebar.slider("传播概率", 0.01, 1.00, 0.30, 0.01, key="infection_prob_slider")
recovery_prob = st.sidebar.slider("恢复概率", 0.01, 1.00, 0.10, 0.01, key="recovery_prob_slider")
rounds = st.sidebar.slider("传播轮数", 5, 50, 20, 1, key="rounds_slider")
seed = st.sidebar.number_input("随机种子", value=42, step=1, key="seed_input")

st.sidebar.subheader("辟谣干预设置")
enable_refutation = st.sidebar.checkbox("启用辟谣机制", value=False, key="enable_refutation_checkbox")
refutation_round = st.sidebar.slider("辟谣开始轮次", 1, 50, 10, 1, key="refutation_round_slider")
refutation_factor = st.sidebar.slider("辟谣后传播概率衰减系数", 0.1, 1.0, 0.5, 0.1, key="refutation_factor_slider")

st.sidebar.subheader("关键节点干预设置")
enable_key_control = st.sidebar.checkbox("限制关键节点传播", value=False, key="enable_key_control_checkbox")
key_control_ratio = st.sidebar.slider("关键节点比例", 0.01, 0.20, 0.05, 0.01, key="key_control_ratio_slider")

# 冲突保护：关键节点作为初始传播源时，不允许同时限制关键节点传播
if source_type == "key" and enable_key_control:
    st.sidebar.warning("已自动关闭“关键节点传播限制”：当初始传播源为关键节点时，两者不能同时生效。")
    enable_key_control = False


# =========================
# 按钮
# =========================
if st.sidebar.button("开始模拟", key="run_sim_button"):
    st.session_state.simulation_result = run_simulation(
        model_type=model_type,
        num_nodes=num_nodes,
        attach_edges=attach_edges,
        infection_prob=infection_prob,
        recovery_prob=recovery_prob,
        rounds=rounds,
        seed=seed,
        source_type=source_type,
        enable_refutation=enable_refutation,
        refutation_round=refutation_round,
        refutation_factor=refutation_factor,
        enable_key_control=enable_key_control,
        key_control_ratio=key_control_ratio,
    )

    baseline_result = run_simulation(
        model_type=model_type,
        num_nodes=num_nodes,
        attach_edges=attach_edges,
        infection_prob=infection_prob,
        recovery_prob=recovery_prob,
        rounds=rounds,
        seed=seed,
        source_type=source_type,
        enable_refutation=False,
        refutation_round=refutation_round,
        refutation_factor=refutation_factor,
        enable_key_control=False,
        key_control_ratio=key_control_ratio,
    )

    refutation_result = run_simulation(
        model_type=model_type,
        num_nodes=num_nodes,
        attach_edges=attach_edges,
        infection_prob=infection_prob,
        recovery_prob=recovery_prob,
        rounds=rounds,
        seed=seed,
        source_type=source_type,
        enable_refutation=True,
        refutation_round=refutation_round,
        refutation_factor=refutation_factor,
        enable_key_control=False,
        key_control_ratio=key_control_ratio,
    )

    key_control_result = run_simulation(
        model_type=model_type,
        num_nodes=num_nodes,
        attach_edges=attach_edges,
        infection_prob=infection_prob,
        recovery_prob=recovery_prob,
        rounds=rounds,
        seed=seed,
        source_type=source_type,
        enable_refutation=False,
        refutation_round=refutation_round,
        refutation_factor=refutation_factor,
        enable_key_control=True,
        key_control_ratio=key_control_ratio,
    )

    st.session_state.comparison_result = {
        "baseline": baseline_result,
        "refutation": refutation_result,
        "key_control": key_control_result,
    }

if st.sidebar.button("运行传播源对比实验", key="run_source_exp_button"):
    random_source_result = run_simulation(
        model_type=model_type,
        num_nodes=num_nodes,
        attach_edges=attach_edges,
        infection_prob=infection_prob,
        recovery_prob=recovery_prob,
        rounds=rounds,
        seed=seed,
        source_type="random",
        enable_refutation=enable_refutation,
        refutation_round=refutation_round,
        refutation_factor=refutation_factor,
        enable_key_control=enable_key_control,
        key_control_ratio=key_control_ratio,
    )

    normal_source_result = run_simulation(
        model_type=model_type,
        num_nodes=num_nodes,
        attach_edges=attach_edges,
        infection_prob=infection_prob,
        recovery_prob=recovery_prob,
        rounds=rounds,
        seed=seed,
        source_type="normal",
        enable_refutation=enable_refutation,
        refutation_round=refutation_round,
        refutation_factor=refutation_factor,
        enable_key_control=enable_key_control,
        key_control_ratio=key_control_ratio,
    )

    key_source_result = run_simulation(
        model_type=model_type,
        num_nodes=num_nodes,
        attach_edges=attach_edges,
        infection_prob=infection_prob,
        recovery_prob=recovery_prob,
        rounds=rounds,
        seed=seed,
        source_type="key",
        enable_refutation=enable_refutation,
        refutation_round=refutation_round,
        refutation_factor=refutation_factor,
        enable_key_control=enable_key_control,
        key_control_ratio=key_control_ratio,
    )

    st.session_state.source_experiment_result = {
        "random": random_source_result,
        "normal": normal_source_result,
        "key": key_source_result,
    }


# =========================
# 主区域
# =========================
result = st.session_state.simulation_result
comparison = st.session_state.comparison_result
source_experiment = st.session_state.source_experiment_result

if result is None:
    st.info("请在左侧设置参数后，点击“开始模拟”。")
else:
    G = result["G"]
    history = result["history"]
    count_history = result["count_history"]
    states_list = result["states_list"]
    blocked_nodes = result["blocked_nodes"]

    I_counts = count_history.get("I", [])
    source_type_text = source_labels.get(source_type, source_type)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("传播峰值人数", result["peak_I"])
    col2.metric("峰值出现轮次", result["peak_round"])
    col3.metric("初始传播源节点", result["initial_node"])

    if "R" in states_list:
        col4.metric("最终停止传播比例", f"{result['final_ratio']:.2%}")
    else:
        col4.metric("当前模型", model_type)

    # =========================
    # 一键导出
    # =========================
    export_params = {
        "model_type": model_type,
        "source_type": source_type_text,
        "num_nodes": num_nodes,
        "attach_edges": attach_edges,
        "infection_prob": infection_prob,
        "recovery_prob": recovery_prob,
        "rounds": rounds,
        "seed": seed,
        "enable_refutation": enable_refutation,
        "refutation_round": refutation_round,
        "refutation_factor": refutation_factor,
        "enable_key_control": enable_key_control,
        "key_control_ratio": key_control_ratio,
    }

    zip_data = build_export_zip(result, export_params)

    st.download_button(
        label="📦 一键导出实验结果",
        data=zip_data,
        file_name="rumor_simulation_result.zip",
        mime="application/zip",
        key="download_export_button"
    )

    st.subheader(f"{model_type} 模型传播曲线")
    fig_curve, ax = plt.subplots(figsize=(8, 5))
    x = range(1, len(I_counts) + 1)

    for state_name in states_list:
        ax.plot(x, count_history[state_name], label=state_name)

    ax.set_title(f"{model_type} 谣言传播曲线")
    ax.set_xlabel("轮次")
    ax.set_ylabel("节点数量")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig_curve)
    plt.close(fig_curve)

    if comparison is not None:
        st.subheader("三种治理策略传播对比")

        baseline_I = comparison["baseline"]["count_history"].get("I", [])
        refutation_I = comparison["refutation"]["count_history"].get("I", [])
        key_control_I = comparison["key_control"]["count_history"].get("I", [])

        fig_compare, ax2 = plt.subplots(figsize=(8, 5))
        ax2.plot(range(1, len(baseline_I) + 1), baseline_I, label="无干预")
        ax2.plot(range(1, len(refutation_I) + 1), refutation_I, label="辟谣干预")
        ax2.plot(range(1, len(key_control_I) + 1), key_control_I, label="关键节点限制")
        ax2.set_title("不同干预策略对比")
        ax2.set_xlabel("轮次")
        ax2.set_ylabel("感染节点数")
        ax2.legend()
        ax2.grid(True)
        st.pyplot(fig_compare)
        plt.close(fig_compare)

        c1, c2, c3 = st.columns(3)
        c1.metric("无干预峰值", comparison["baseline"]["peak_I"])
        c2.metric("辟谣干预峰值", comparison["refutation"]["peak_I"])
        c3.metric("关键节点限制峰值", comparison["key_control"]["peak_I"])

    if source_experiment is not None:
        st.subheader("不同传播源类型对比实验")

        random_I = source_experiment["random"]["count_history"].get("I", [])
        normal_I = source_experiment["normal"]["count_history"].get("I", [])
        key_I = source_experiment["key"]["count_history"].get("I", [])

        fig_source, ax3 = plt.subplots(figsize=(8, 5))
        ax3.plot(range(1, len(random_I) + 1), random_I, label=source_labels["random"])
        ax3.plot(range(1, len(normal_I) + 1), normal_I, label=source_labels["normal"])
        ax3.plot(range(1, len(key_I) + 1), key_I, label=source_labels["key"])
        ax3.set_title("不同传播源类型对比")
        ax3.set_xlabel("轮次")
        ax3.set_ylabel("感染节点数")
        ax3.legend()
        ax3.grid(True)
        st.pyplot(fig_source)
        plt.close(fig_source)

        s1, s2, s3 = st.columns(3)
        s1.metric("随机节点峰值", source_experiment["random"]["peak_I"])
        s2.metric("普通节点峰值", source_experiment["normal"]["peak_I"])
        s3.metric("关键节点峰值", source_experiment["key"]["peak_I"])

    st.subheader("网络扩散动态展示")

    pos = nx.spring_layout(G, seed=42)

    round_index = st.slider("查看传播轮次", 0, len(history) - 1, 0, 1, key="round_slider")
    fig_network = draw_network_frame(
        G,
        history[round_index],
        pos,
        f"第{round_index}轮",
        blocked_nodes=blocked_nodes
    )
    st.pyplot(fig_network)
    plt.close(fig_network)

    if st.button("播放传播动画", key="play_animation_button"):
        placeholder = st.empty()

        for i, state in enumerate(history):
            fig = draw_network_frame(
                G,
                state,
                pos,
                f"第{i}轮",
                blocked_nodes=blocked_nodes
            )
            placeholder.pyplot(fig)
            plt.close(fig)
            time.sleep(0.5)

    st.subheader("结果分析")

    analysis_text = (
        f"当前选择的传播模型为 **{model_type}**，"
        f"初始传播源类型为 **{source_type_text}**。"
        f"本次模拟中，谣言在第 **{result['peak_round']}** 轮达到传播峰值，"
        f"峰值传播人数为 **{result['peak_I']}** 人。"
    )

    if "R" in states_list:
        analysis_text += (
            f"最终共有 **{result['final_R']}** 个节点停止传播，"
            f"占总节点数的 **{result['final_ratio']:.2%}**。"
        )

    if comparison is not None:
        baseline_peak = comparison["baseline"]["peak_I"]
        refutation_peak = comparison["refutation"]["peak_I"]
        key_control_peak = comparison["key_control"]["peak_I"]

        analysis_text += (
            f"在本组实验中，无干预场景的峰值为 **{baseline_peak}**，"
            f"辟谣干预后的峰值为 **{refutation_peak}**，"
            f"关键节点限制后的峰值为 **{key_control_peak}**。"
        )

        if key_control_peak < refutation_peak:
            analysis_text += "结果表明，限制关键节点传播在当前网络结构下表现出更强的抑制效果。"
        elif key_control_peak > refutation_peak:
            analysis_text += "结果表明，辟谣干预在当前参数设置下表现出更强的抑制效果。"
        else:
            analysis_text += "结果表明，两种干预策略在当前参数设置下效果接近。"

    if source_experiment is not None:
        random_peak = source_experiment["random"]["peak_I"]
        normal_peak = source_experiment["normal"]["peak_I"]
        key_peak = source_experiment["key"]["peak_I"]

        analysis_text += (
            f"在传播源对比实验中，随机节点的峰值为 **{random_peak}**，"
            f"普通节点的峰值为 **{normal_peak}**，"
            f"关键节点的峰值为 **{key_peak}**。"
        )

        if key_peak >= random_peak and key_peak >= normal_peak:
            analysis_text += "结果表明，从关键节点发起传播更容易引发大规模扩散，说明关键节点在无标度网络中具有显著的传播放大效应。"
        elif normal_peak <= random_peak and normal_peak <= key_peak:
            analysis_text += "结果表明，从普通节点发起传播时扩散范围相对较弱。"

    st.write(analysis_text)
