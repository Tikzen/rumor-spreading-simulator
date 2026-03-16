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


def create_comparison_figure(comparison_result: dict):
    """
    生成三种治理策略对比图
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    baseline_I = comparison_result.get("baseline", {}).get("count_history", {}).get("I", [])
    refutation_I = comparison_result.get("refutation", {}).get("count_history", {}).get("I", [])
    key_control_I = comparison_result.get("key_control", {}).get("count_history", {}).get("I", [])

    ax.plot(range(1, len(baseline_I) + 1), baseline_I, label="No Intervention")
    ax.plot(range(1, len(refutation_I) + 1), refutation_I, label="Refutation")
    ax.plot(range(1, len(key_control_I) + 1), key_control_I, label="Key Node Control")

    ax.set_title("Strategy Comparison")
    ax.set_xlabel("Round")
    ax.set_ylabel("Infected Nodes")
    ax.legend()
    ax.grid(True)

    return fig


def create_source_experiment_figure(source_experiment_result: dict):
    """
    生成不同传播源类型对比图
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    random_I = source_experiment_result.get("random", {}).get("count_history", {}).get("I", [])
    normal_I = source_experiment_result.get("normal", {}).get("count_history", {}).get("I", [])
    key_I = source_experiment_result.get("key", {}).get("count_history", {}).get("I", [])

    ax.plot(range(1, len(random_I) + 1), random_I, label="Random Source")
    ax.plot(range(1, len(normal_I) + 1), normal_I, label="Normal Source")
    ax.plot(range(1, len(key_I) + 1), key_I, label="Key Source")

    ax.set_title("Source Type Comparison")
    ax.set_xlabel("Round")
    ax.set_ylabel("Infected Nodes")
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


def report_to_text(
    result: dict,
    params: dict = None,
    comparison_result: dict = None,
    source_experiment_result: dict = None
) -> str:
    """
    自动生成实验报告文本
    """
    model_type = params.get("model_type", "Unknown") if params else "Unknown"
    source_type = params.get("source_type", "Unknown") if params else "Unknown"

    peak_i = result.get("peak_I", 0)
    peak_round = result.get("peak_round", 0)
    final_r = result.get("final_R", 0)
    final_ratio = result.get("final_ratio", 0)

    lines = ["Experiment Report"]
    lines.append("=" * 24)
    lines.append("")
    lines.append("1. Basic Information")
    lines.append("-" * 24)
    lines.append(f"Model type: {model_type}")
    lines.append(f"Source type: {source_type}")
    if params:
        lines.append(f"Node count: {params.get('num_nodes')}")
        lines.append(f"Infection probability: {params.get('infection_prob')}")
        lines.append(f"Recovery probability: {params.get('recovery_prob')}")
        lines.append(f"Rounds: {params.get('rounds')}")
    lines.append("")

    lines.append("2. Main Results")
    lines.append("-" * 24)
    lines.append(f"Peak infected count: {peak_i}")
    lines.append(f"Peak round: {peak_round}")
    lines.append(f"Final recovered/stopped count: {final_r}")
    lines.append(f"Final stopped ratio: {final_ratio:.2%}")
    lines.append("")

    lines.append("3. Analysis")
    lines.append("-" * 24)
    lines.append(
        f"In this experiment, the rumor reached its maximum spread at round {peak_round}, "
        f"with {peak_i} infected nodes."
    )
    lines.append(
        f"Finally, {final_r} nodes stopped spreading, accounting for {final_ratio:.2%} of all nodes."
    )

    if comparison_result is not None:
        baseline_peak = comparison_result.get("baseline", {}).get("peak_I", 0)
        refutation_peak = comparison_result.get("refutation", {}).get("peak_I", 0)
        key_control_peak = comparison_result.get("key_control", {}).get("peak_I", 0)

        lines.append("")
        lines.append("Intervention comparison:")
        lines.append(f"- No intervention peak: {baseline_peak}")
        lines.append(f"- Refutation peak: {refutation_peak}")
        lines.append(f"- Key node control peak: {key_control_peak}")

        if key_control_peak < refutation_peak:
            lines.append("Key node control performs better under current settings.")
        elif key_control_peak > refutation_peak:
            lines.append("Refutation performs better under current settings.")
        else:
            lines.append("The two intervention strategies perform similarly under current settings.")

    if source_experiment_result is not None:
        random_peak = source_experiment_result.get("random", {}).get("peak_I", 0)
        normal_peak = source_experiment_result.get("normal", {}).get("peak_I", 0)
        key_peak = source_experiment_result.get("key", {}).get("peak_I", 0)

        lines.append("")
        lines.append("Source type comparison:")
        lines.append(f"- Random source peak: {random_peak}")
        lines.append(f"- Normal source peak: {normal_peak}")
        lines.append(f"- Key source peak: {key_peak}")

        if key_peak >= random_peak and key_peak >= normal_peak:
            lines.append("Key nodes are more likely to trigger large-scale spreading.")
        elif normal_peak <= random_peak and normal_peak <= key_peak:
            lines.append("Normal nodes lead to weaker spreading.")
        else:
            lines.append("Different source types significantly affect spreading scale.")

    lines.append("")
    lines.append("4. Conclusion")
    lines.append("-" * 24)
    lines.append(
        "The system can effectively simulate rumor spreading in social networks and support strategy analysis."
    )

    return "\n".join(lines)


def build_export_zip(
    result: dict,
    params: dict = None,
    comparison_result: dict = None,
    source_experiment_result: dict = None
) -> bytes:
    """
    构建导出 ZIP
    包含：
    - simulation_result.csv
    - spread_curve.png
    - parameters.txt
    - summary.txt
    - experiment_report.txt
    - comparison_curve.png（可选）
    - source_experiment_curve.png（可选）
    """
    zip_buffer = BytesIO()

    # 主实验结果表格
    result_df = build_result_dataframe(result)
    csv_bytes = dataframe_to_csv_bytes(result_df)

    # 主传播曲线图
    fig = create_curve_figure(result)
    png_bytes = figure_to_png_bytes(fig)

    # 参数文本
    params_text = params_to_text(params).encode("utf-8")

    # 摘要文本
    summary_text = summary_to_text(result).encode("utf-8")

    # 实验报告文本
    report_text = report_to_text(
        result,
        params=params,
        comparison_result=comparison_result,
        source_experiment_result=source_experiment_result
    ).encode("utf-8")

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("simulation_result.csv", csv_bytes)
        zf.writestr("spread_curve.png", png_bytes)
        zf.writestr("parameters.txt", params_text)
        zf.writestr("summary.txt", summary_text)
        zf.writestr("experiment_report.txt", report_text)

        if comparison_result is not None:
            comparison_fig = create_comparison_figure(comparison_result)
            comparison_png = figure_to_png_bytes(comparison_fig)
            zf.writestr("comparison_curve.png", comparison_png)

        if source_experiment_result is not None:
            source_fig = create_source_experiment_figure(source_experiment_result)
            source_png = figure_to_png_bytes(source_fig)
            zf.writestr("source_experiment_curve.png", source_png)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()
