##
基于本项目的差分升级版本现已推出
https://github.com/Tikzen/Public-Opinion-Statistical-Modeling
新增页面:
Parameter Estimation：
用于反演β与γ参数，提供多种拟合方式并自带归一化算法（依赖有所增加），参数调节方法与Simulator相同
AI Analysis（此页面需要自行配置apikey）：
提供了基础的数据抓取工具，支持从预设的网页（目前仅支持kaggle）抓取信息，AI会辅助数据处理与分析
接入大模型 帮助分析参数，帮助另外两个页面的使用，并支持从Parameter Estimation中直接接收参数，提供可读性更强的分析并提供参数策略。
#
## Quick Start
pip install -r requirements.txt
streamlit run Home.py

# Rumor Propagation Simulator  
## 社交网络谣言传播与干预策略模拟平台

本项目是一个基于复杂网络的 **信息传播仿真系统**，用于模拟谣言在社交网络中的扩散过程，并分析不同干预策略对传播效果的影响。

系统支持多种传播模型，并提供可视化传播过程、传播曲线分析以及干预策略对比实验。

---

# 功能特点

## 1 多传播模型支持
系统支持多种经典传播模型：

- SI 模型
- SIS 模型
- SIR 模型

系统采用 **插件化模型架构**，用户可以在 `model/` 目录中添加新的模型文件，系统会自动识别并加载。

---

## 2 社交网络模拟

系统使用复杂网络模型模拟真实社交网络结构：

- Barabási-Albert 无标度网络

网络特点：

- 少数节点拥有大量连接
- 大多数节点连接较少

符合真实社交媒体网络结构。

---

## 3 干预策略模拟

系统支持多种治理策略：

### 辟谣机制

在指定轮次降低传播概率：


infection_prob *= refutation_factor


模拟官方辟谣后的传播抑制效果。

---

### 关键节点控制

识别网络中的高中心性节点并限制其传播能力：

- 使用 **degree centrality** 识别关键节点
- 阻断关键节点传播

---

## 4 传播源实验

系统支持不同传播源类型：

- 随机节点
- 普通节点
- 关键节点

用于研究：

> 谣言从不同节点类型开始传播时的扩散差异。

---

## 5 可视化分析

系统提供多种可视化方式：

### 传播曲线

展示：


S - 未感染节点
I - 传播节点
R - 停止传播节点


---

### 网络传播动画

展示谣言在网络中的动态扩散过程。

---

### 干预策略对比

比较不同治理策略：

- 无干预
- 辟谣干预
- 关键节点限制

---

### 传播源对比实验

比较：

- 随机传播源
- 普通节点传播源
- 关键节点传播源

---

# 项目结构


Rumor-Spreading-Simulator
│
├─ model/ # 传播模型插件
│ ├─ si_model.py
│ ├─ sis_model.py
│ ├─ sir_model.py
│ └─ template_model.py
│
├─ network/
│ └─ generator.py # 网络生成模块
│
├─ ui/
│ └─ app.py # Streamlit Web界面
│
├─ visualization/ # 可视化模块
│
└─ README.md


---

# 运行方法

安装依赖：


pip install streamlit networkx matplotlib numpy


运行系统：


streamlit run ui/app.py


浏览器访问：


http://localhost:8501


---

# 模型扩展

系统支持自定义传播模型。

只需在 `model/` 目录中添加新的 `.py` 文件，并遵循统一接口规范。

详见：


model/README.md


---

# 项目目标

本系统旨在提供一个 **可扩展的信息传播仿真平台**，用于研究：

- 谣言扩散规律
- 网络结构对传播的影响
- 不同干预策略的效果

适用于：

- 计算机设计大赛
- 复杂网络研究

- 信息传播模拟实验

