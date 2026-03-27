import { Type } from "@sinclair/typebox";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";

type ResumePluginConfig = {
  greeting?: string;
  shout?: boolean;
};

function parsePluginConfig(value: unknown): ResumePluginConfig {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};
  const raw = value as Record<string, unknown>;
  return {
    greeting: typeof raw.greeting === "string" ? raw.greeting : undefined,
    shout: typeof raw.shout === "boolean" ? raw.shout : undefined,
  };
}

const ResumeEchoToolSchema = Type.Object(
  {
    text: Type.String({ description: "Text to echo back" }),
    times: Type.Optional(
      Type.Integer({
        description: "Repeat count (1-5)",
        minimum: 1,
        maximum: 5,
        default: 1,
      }),
    ),
  },
  { additionalProperties: false },
);

const plugin = {
  id: "resume-plugin",
  name: "Resume Plugin",
  description: "Resume templating + import helpers (render DOCX from template.docx + data.json).",

  // Note: config validation happens via openclaw.plugin.json (manifest).
  register(api: OpenClawPluginApi) {
    const cfg = parsePluginConfig(api.pluginConfig);
    const greeting = cfg.greeting ?? "Hello from resume-plugin!";
    const shout = cfg.shout ?? false;

    const format = (s: string) => (shout ? s.toUpperCase() : s);

    // 1) Auto-reply command: /resume [anything]
    api.registerCommand({
      name: "resume",
      description: "Demo command from resume-plugin. Usage: /resume hello",
      acceptsArgs: true,
      requireAuth: false,
      handler: (ctx) => {
        const arg = (ctx.args ?? "").trim();
        const msg = arg ? `${greeting} You said: ${arg}` : greeting;
        return { text: format(msg) };
      },
    });

    // 2) Agent tool (optional): resume_echo
    api.registerTool(
      {
        name: "resume_echo",
        label: "Resume Echo",
        description: "Echo back a message (demo tool from resume-plugin).",
        parameters: ResumeEchoToolSchema,
        async execute(_toolCallId, params) {
          const text = String((params as any).text ?? "");
          const timesRaw = Number((params as any).times ?? 1);
          const times = Number.isFinite(timesRaw) ? Math.min(5, Math.max(1, timesRaw)) : 1;
          const out = Array.from({ length: times }, () => text).join("\n");
          return {
            content: [{ type: "text", text: format(out) }],
            details: { echoed: text, times },
          };
        },
      },
      { optional: true },
    );

    // 3) Gateway RPC method: resumeplugin.ping
    api.registerGatewayMethod("resumeplugin.ping", ({ respond }) => {
      respond(true, {
        ok: true,
        plugin: "resume-plugin",
        ts: Date.now(),
      });
    });

    // 4) CLI: openclaw resume-plugin ping
    api.registerCli(
      ({ program }) => {
        const cmd = program.command("resume-plugin").description("Commands from the resume-plugin");

        cmd
          .command("ping")
          .description("Print a local pong (does not call the Gateway)")
          .action(() => {
            console.log("pong (resume-plugin)");
          });

        cmd
          .command("show-config")
          .description("Print the parsed plugin config")
          .action(() => {
            console.log(JSON.stringify({ greeting, shout }, null, 2));
          });
      },
      { commands: ["resume-plugin"] },
    );

    // 5) CLI: openclaw resume parse
    // Renders a DOCX using template.docx + data.json into result.docx.
    // Template syntax matches the resume-pdf-import skill:
    //   - variables: {name}
    //   - sections: {#skills}...{/skills}
    api.registerCli(
      ({ program }) => {
        program
          .command("resume")
          .description("Resume templating helpers")
          .command("parse")
          .description("Render a resume DOCX using a template.docx and data.json")
          .requiredOption("--template <path>", "Path to template .docx")
          .requiredOption("--data <path>", "Path to data .json")
          .requiredOption("--output <path>", "Output .docx path")
          .action(async (opts) => {
            const fs = await import("node:fs/promises");
            const path = await import("node:path");
            const Docxtemplater = (await import("docxtemplater")).default;
            const PizZip = (await import("pizzip")).default;

            const templatePath = path.resolve(String((opts as any).template));
            const dataPath = path.resolve(String((opts as any).data));
            const outputPath = path.resolve(String((opts as any).output));

            const [templateBuf, dataRaw] = await Promise.all([
              fs.readFile(templatePath),
              fs.readFile(dataPath, "utf8"),
            ]);

            let data: any;
            try {
              data = JSON.parse(dataRaw);
            } catch {
              throw new Error(`Failed to parse JSON from --data: ${dataPath}`);
            }

            const zip = new PizZip(templateBuf);
            const doc = new Docxtemplater(zip, {
              paragraphLoop: true,
              linebreaks: true,
              delimiters: { start: "{", end: "}" },
            });

            doc.setData(data);

            try {
              doc.render();
            } catch (e: any) {
              const msg = e?.message ?? String(e);
              throw new Error(`Template render failed: ${msg}`);
            }

            const outBuf = doc.getZip().generate({ type: "nodebuffer" });
            await fs.mkdir(path.dirname(outputPath), { recursive: true });
            await fs.writeFile(outputPath, outBuf);
            console.log(outputPath);
          });
      },
      { commands: ["resume"] },
    );

    // 6) Background service
    api.registerService({
      id: "resume-plugin",
      start: () => {
        api.logger.info(`[resume-plugin] started (greeting=${JSON.stringify(greeting)})`);
      },
      stop: () => {
        api.logger.info("[resume-plugin] stopped");
      },
    });
  },
};

export default plugin;
