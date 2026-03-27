# resume-plugin

An **OpenClaw resume plugin** that can render a DOCX using a `template.docx` + `data.json` (the format used by the `resume-pdf-import` skill).

It includes:

- a **plugin manifest** (`openclaw.plugin.json`)
- a **DOCX render CLI** (`openclaw resume parse ...`)
- a small **CLI namespace** (`openclaw resume-plugin ...`)
- optional demo **command/tool/RPC** surfaces

## Install (local dev)

Clone this repo, then install/link it into OpenClaw extensions:

```bash
# from your openclaw host
git clone <YOUR_GITHUB_URL>
cd resume

# link for development (no copy)
openclaw plugins install -l .

# or copy-install
# openclaw plugins install .

openclaw plugins list
```

Then enable it in your OpenClaw config and restart the Gateway.

### Config

Add this to your `config.json5`:

```js
{
  plugins: {
    entries: {
      "resume-plugin": {
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

Restart:

```bash
openclaw gateway restart
```

## Use

### 1) Command

Send in any connected chat:

- `/resume`
- `/resume hello openclaw`

### 2) CLI

```bash
openclaw resume ping
openclaw resume show-config

# render a docx
openclaw resume parse --template template/template.docx --data template/data.json --output output/result.docx
```

### 3) Tool (optional)

This plugin registers an **optional** tool `resume_echo`. Optional tools are **not enabled by default**.

Enable it (example) on the `main` agent:

```js
{
  agents: {
    list: [
      {
        id: "main",
        tools: {
          allow: ["resume_echo"],
        },
      },
    ],
  },
}
```

Then ask your agent to call it, e.g.:

> Use the tool `resume_echo` to repeat "hi" 3 times.

## Development notes

- The manifest (`openclaw.plugin.json`) is used for **config validation without executing code**.
- `index.ts` is loaded at runtime via **jiti** (TypeScript is OK).

## License

MIT
