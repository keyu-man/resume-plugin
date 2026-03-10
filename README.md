# plugin-first

A tiny **OpenClaw plugin** meant for learning /快速上手.

It demonstrates, in the smallest possible codebase:

- a **plugin manifest** (`openclaw.plugin.json`)
- an **auto-reply command** (`/first`)
- an **agent tool** (`first_echo`, optional/opt-in)
- a **Gateway RPC method** (`pluginfirst.ping`)
- a **CLI command** (`openclaw plugin-first ...`)
- a minimal **background service** (logs start/stop)

## Install (local dev)

Clone this repo, then install/link it into OpenClaw extensions:

```bash
# from your openclaw host
git clone <YOUR_GITHUB_URL>
cd plugin-first

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

Restart:

```bash
openclaw gateway restart
```

## Use

### 1) Command

Send in any connected chat:

- `/first`
- `/first hello openclaw`

### 2) CLI

```bash
openclaw plugin-first ping
openclaw plugin-first show-config
```

### 3) Tool (optional)

This plugin registers an **optional** tool `first_echo`. Optional tools are **not enabled by default**.

Enable it (example) on the `main` agent:

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

Then ask your agent to call it, e.g.:

> Use the tool `first_echo` to repeat "hi" 3 times.

## Development notes

- The manifest (`openclaw.plugin.json`) is used for **config validation without executing code**.
- `index.ts` is loaded at runtime via **jiti** (TypeScript is OK).

## License

MIT
