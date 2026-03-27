# plugin-first

一个用于学习/快速上手的 **OpenClaw 插件**（极简示例）。

它在尽可能小的代码量里演示了：

- **插件清单（manifest）**：`openclaw.plugin.json`
- 一个**自动回复命令**：`/first`
- 一个 **Agent 工具**：`first_echo`（可选/需显式启用）
- 一个 **Gateway RPC 方法**：`pluginfirst.ping`
- 一个 **CLI 命令**：`openclaw plugin-first ...`
- 一个最小化的**后台服务**（打印 start/stop 日志）

## 安装（本地开发）

克隆仓库，然后将其安装/链接到 OpenClaw 的 extensions：

```bash
# 在你的 openclaw 主机上
git clone <YOUR_GITHUB_URL>
cd plugin-first

# 以“开发链接”方式安装（不复制目录）
openclaw plugins install -l .

# 或者：复制安装
# openclaw plugins install .

openclaw plugins list
```

然后在 OpenClaw 配置中启用它，并重启 Gateway。

### 配置

把下面内容加入你的 `config.json5`：

```js
{
  plugins: {
    entries: {
      "plugin-first": {
        enabled: true,
        config: {
          greeting: "Hello!",
          shout: false,
        },
      },
    },
  },
}
```

重启：

```bash
openclaw gateway restart
```

## 使用

### 1）命令

在任意已连接的聊天里发送：

- `/first`
- `/first hello openclaw`

### 2）CLI

```bash
openclaw plugin-first ping
openclaw plugin-first show-config
```

### 3）工具（可选）

本插件注册了一个**可选**工具 `first_echo`。可选工具**默认不会启用**。

在 `main` agent 上启用它（示例）：

```js
{
  agents: {
    list: [
      {
        id: "main",
        tools: {
          allow: ["first_echo"],
        },
      },
    ],
  },
}
```

然后让你的 agent 调用它，例如：

> 使用工具 `first_echo` 把 “hi” 重复 3 次。

## 开发说明

- 插件清单（`openclaw.plugin.json`）用于**在不执行代码的前提下**做配置校验。
- `index.ts` 由运行时通过 **jiti** 加载（支持 TypeScript）。

## License

MIT
