import streamlit as st

st.set_page_config(
    page_title="Rumor Propagation Simulator",
    page_icon="📡",
    layout="wide"
)

# =========================
# Language Switch
# =========================
lang = st.sidebar.selectbox(
    "Language / 语言",
    ["中文", "English"]
)

is_cn = lang == "中文"

# =========================
# Text Dictionary
# =========================
TEXT = {
    "title": "📡 社交网络谣言传播与干预策略模拟平台" if is_cn else "📡 Rumor Propagation Simulation Platform",
    "subtitle": "基于复杂网络与多传播模型的信息扩散仿真系统" if is_cn else "A Complex Network Based Information Diffusion Simulator",

    "overview": "项目简介" if is_cn else "Project Overview",
    "overview_text": (
        """
        本系统面向社交网络中的信息扩散问题，基于复杂网络理论与经典传播模型，
        构建了一个可交互、可扩展的谣言传播模拟平台。

        用户可以通过网页界面设置网络规模、传播概率、恢复概率、传播轮数等参数，
        并选择不同传播模型与不同治理策略，观察谣言在网络中的传播过程及其变化趋势。

        系统支持传播动画、传播曲线、策略对比和传播源实验，能够直观展示谣言扩散规律，
        并辅助分析辟谣机制、关键节点治理等干预手段的效果。
        """
        if is_cn else
        """
        This platform simulates rumor propagation in social networks using
        classical epidemic spreading models and complex network theory.

        Users can configure network size, spreading probability, recovery probability,
        propagation rounds, and different intervention strategies through an interactive interface.

        The system supports propagation animation, spreading curves, strategy comparison,
        and source-type experiments, helping users intuitively understand rumor diffusion
        dynamics and the effectiveness of intervention mechanisms.
        """
    ),

    "quick_start": "快速入口" if is_cn else "Quick Start",
    "open_simulator": "进入模拟系统" if is_cn else "Open Simulator",
    "demo_steps": (
        """
        建议演示顺序：

        1. 进入模拟系统  
        2. 选择传播模型  
        3. 调整参数并运行  
        4. 查看传播动画与曲线  
        5. 运行对比实验
        """
        if is_cn else
        """
        Suggested demo steps:

        1. Open Simulator  
        2. Select propagation model  
        3. Adjust parameters  
        4. Run simulation  
        5. Compare strategies
        """
    ),

    "features": "系统功能" if is_cn else "Key Features",

    "feature_model_title": "传播模型" if is_cn else "Propagation Models",
    "feature_model_text": (
        """
        - SI 模型  
        - SIS 模型  
        - SIR 模型  
        - 支持自定义模型扩展
        """
        if is_cn else
        """
        - SI Model  
        - SIS Model  
        - SIR Model  
        - Custom Model Extension
        """
    ),

    "feature_strategy_title": "干预策略" if is_cn else "Intervention Strategies",
    "feature_strategy_text": (
        """
        - 辟谣机制  
        - 关键节点限制  
        - 多策略传播效果对比
        """
        if is_cn else
        """
        - Rumor Refutation  
        - Key Node Restriction  
        - Multi-strategy Comparison
        """
    ),

    "feature_vis_title": "可视化分析" if is_cn else "Visualization",
    "feature_vis_text": (
        """
        - 传播曲线  
        - 网络扩散动态展示  
        - 传播源对比实验
        """
        if is_cn else
        """
        - Propagation Curves  
        - Network Diffusion Animation  
        - Source Type Comparison
        """
    ),

    "innovation": "创新亮点" if is_cn else "Innovation Highlights",

    "innovation_1_title": "插件化模型架构" if is_cn else "Plugin-based Model Architecture",
    "innovation_1_text": (
        """
        系统采用插件化传播模型架构。
        用户只需将新的模型文件加入 `model/` 目录，
        即可扩展系统，而无需修改主程序逻辑。

        这种设计提升了平台的可扩展性与可塑性。
        """
        if is_cn else
        """
        The simulator adopts a modular plugin architecture for propagation models.
        Users can extend the system by simply adding new model files into the `model/`
        directory without modifying the main program.

        This design improves scalability and flexibility.
        """
    ),

    "innovation_2_title": "多策略干预模拟" if is_cn else "Multi-strategy Intervention Simulation",
    "innovation_2_text": (
        """
        系统支持多种治理策略，包括：

        - 辟谣机制  
        - 关键节点传播限制  
        - 多策略对比实验  

        便于研究不同治理方式对谣言扩散的抑制效果。
        """
        if is_cn else
        """
        The platform supports multiple governance strategies including:

        - rumor refutation mechanisms  
        - key node propagation restriction  
        - strategy comparison experiments  

        These features help analyze the effectiveness of different rumor mitigation approaches.
        """
    ),

    "innovation_3_title": "交互式可视化平台" if is_cn else "Interactive Visualization Platform",
    "innovation_3_text": (
        """
        系统提供多种可视化手段：

        - 传播曲线  
        - 网络扩散动画  
        - 传播源对比实验  

        用户可以直观理解复杂网络中的谣言传播规律。
        """
        if is_cn else
        """
        The system provides multiple visualization tools:

        - propagation curves  
        - network diffusion animation  
        - source type comparison experiments  

        These visualizations help users intuitively understand rumor spreading dynamics
        in complex networks.
        """
    ),

    "run_title": "运行方式" if is_cn else "Run the Platform",
    "run_success": "点击右侧“进入模拟系统”即可跳转到主仿真页面。" if is_cn else "Click 'Open Simulator' to enter the main simulation page.",
}

# =========================
# Page Content
# =========================
st.title(TEXT["title"])
st.markdown(f"### {TEXT['subtitle']}")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(TEXT["overview"])
    st.write(TEXT["overview_text"])

with col2:
    st.subheader(TEXT["quick_start"])
    st.page_link("pages/simulator.py", label=TEXT["open_simulator"], icon="🚀")
    st.info(TEXT["demo_steps"])

st.divider()

st.subheader(TEXT["features"])

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"#### {TEXT['feature_model_title']}")
    st.markdown(TEXT["feature_model_text"])

with c2:
    st.markdown(f"#### {TEXT['feature_strategy_title']}")
    st.markdown(TEXT["feature_strategy_text"])

with c3:
    st.markdown(f"#### {TEXT['feature_vis_title']}")
    st.markdown(TEXT["feature_vis_text"])

st.divider()

st.subheader(TEXT["innovation"])

i1, i2, i3 = st.columns(3)

with i1:
    st.markdown(f"**{TEXT['innovation_1_title']}**")
    st.write(TEXT["innovation_1_text"])

with i2:
    st.markdown(f"**{TEXT['innovation_2_title']}**")
    st.write(TEXT["innovation_2_text"])

with i3:
    st.markdown(f"**{TEXT['innovation_3_title']}**")
    st.write(TEXT["innovation_3_text"])

st.divider()

st.subheader(TEXT["run_title"])

st.code(
    """pip install -r requirements.txt
streamlit run Home.py""",
    language="bash"
)

st.success(TEXT["run_success"])