# 模型开发规范

本系统采用 **插件化传播模型架构**。

用户可以通过在 `model/` 目录中添加新的模型文件来扩展系统。

系统会自动扫描该目录并加载符合规范的模型。

---

# 模型文件结构

每个模型文件必须包含以下三个内容：

## 1 模型名称


MODEL_NAME = "SIR"


用于在界面中显示模型名称。

---

## 2 状态列表


STATES = ["S", "I", "R"]


表示模型中的节点状态。

例如：

| 状态 | 含义 |
|-----|------|
| S | 未接触信息 |
| I | 正在传播 |
| R | 停止传播 |

---

## 3 传播函数


def step(G, state, infection_prob, recovery_prob, blocked_nodes=None):


参数说明：

| 参数 | 含义 |
|----|----|
| G | 社交网络图 |
| state | 节点状态字典 |
| infection_prob | 传播概率 |
| recovery_prob | 恢复概率 |
| blocked_nodes | 被限制传播的节点 |

函数返回：


new_state


新的节点状态。

---

# 示例


MODEL_NAME = "SIR"
STATES = ["S", "I", "R"]

def step(...):
...


---

# 新模型添加步骤

1 创建新文件：


model/seir_model.py


2 按模板实现模型

3 重新启动系统

新模型会自动出现在界面中。

---

# 推荐模型

可以实现的传播模型：

- SEIR
- SIRS
- Independent Cascade
- Threshold Model