import zipfile
from io import BytesIO

import pandas as pd
import matplotlib.pyplot as plt


def build_result_dataframe(result: dict) -> pd.DataFrame:
    """
    根据 simulator.py 的 simulation_result 构建导出表格
    导出字段按每一轮各状态节点数量组织
    """
    count_history = result.get("count_history", {})
    states_list = result.get("states_list", [])

    max_len = 0
    for state_name in states_list:
        max_len = max(max_len, len(count_history.get(state_name, [])))

    data = {
        "round": list(range(1, max_len + 1))
    }

    for state_name in states_list:
        values = count_history.get(state_name, [])
        if len(values) < max_len:
            values = values + [0] * (max_len - len(values))
        data[state_name] = values

    df = pd.DataFrame(data)
    return df


def create_curve_figure(result: dict):
    """
    生成传播曲线图
    """
    count_history = result.get("count_history", {})
    states_list = result.get("states_list", [])

    fig, ax = plt.subplots(figsize=(8, 5))

    max_len = 0
    for state_name in states_list:
        max_len = max(max_len, len(count_history.get(state_name, [])))

    x = list(range(1, max_len + 1))

    for state_name in states_list:
        y = count_history.get(state_name, [])
        if len(y) < max_len:
            y = y + [0] * (max_len - len(y))
        ax.plot(x, y, label=state_name)

    ax.set_title("Rumor Propagation Curve")
    ax.set_xlabel("Round")
    ax.set_ylabel("Number of Nodes")
    ax.legend()
    ax.grid(True)

    return fig


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """
    DataFrame 转 CSV 字节流
    utf-8-sig 方便 Excel 直接打开中文不乱码
    """
    return df.to_csv(index=False).encode("utf-8-sig")


def figure_to_png_bytes(fig) -> bytes:
    """
    matplotlib 图像转 PNG 字节流
    """
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
    buffer.seek(0)
    png_bytes = buffer.read()
    buffer.close()
    plt.close(fig)
    return png_bytes


def params_to_text(params: dict) -> str:
    """
    将参数字典转为文本
    """
    if not params:
        return "No parameters provided."

    lines = ["Simulation Parameters"]
    lines.append("=" * 24)

    for key, value in params.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def summary_to_text(result: dict) -> str:
    """
    将关键结果转为摘要文本
    """
    peak_i = result.get("peak_I", 0)
    peak_round = result.get("peak_round", 0)
    final_r = result.get("final_R", 0)
    final_ratio = result.get("final_ratio", 0)
    initial_node = result.get("initial_node", None)
    blocked_nodes = result.get("blocked_nodes", set())

    lines = ["Simulation Summary"]
    lines.append("=" * 18)
    lines.append(f"Initial source node: {initial_node}")
    lines.append(f"Peak infected count: {peak_i}")
    lines.append(f"Peak round: {peak_round}")
    lines.append(f"Final recovered/stopped count: {final_r}")
    lines.append(f"Final stopped ratio: {final_ratio:.2%}")
    lines.append(f"Blocked key nodes count: {len(blocked_nodes)}")

    return "\n".join(lines)


def build_export_zip(result: dict, params: dict = None) -> bytes:
    """
    构建导出 ZIP
    包含：
    - simulation_result.csv
    - spread_curve.png
    - parameters.txt
    - summary.txt
    """
    zip_buffer = BytesIO()

    # 结果表格
    result_df = build_result_dataframe(result)
    csv_bytes = dataframe_to_csv_bytes(result_df)

    # 曲线图
    fig = create_curve_figure(result)
    png_bytes = figure_to_png_bytes(fig)

    # 参数文本
    params_text = params_to_text(params).encode("utf-8")

    # 摘要文本
    summary_text = summary_to_text(result).encode("utf-8")

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("simulation_result.csv", csv_bytes)
        zf.writestr("spread_curve.png", png_bytes)
        zf.writestr("parameters.txt", params_text)
        zf.writestr("summary.txt", summary_text)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()