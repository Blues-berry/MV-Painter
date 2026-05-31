# MV-Painter 项目

## 图片处理规则（重要）

主模型 `sonnet`（mimo-v2.5-pro）**不支持视觉**。读取图片时必须通过 Agent 工具委派给 `image-reader` 智能体，并**显式指定 `model: "opus"`**：

```
Agent(subagent_type="image-reader", model="opus", prompt="请读取并描述 /path/to/image.png")
```

关键：必须传 `model="opus"` 参数，否则智能体会继承主模型的 mimo-v2.5-pro 导致报错。

**禁止**使用 Python 脚本通过 `localhost:8000` 连接本地模型服务，该服务未运行。
