import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import process from "node:process";
import stripAnsi from "strip-ansi";

function getArg(name) {
  const ix = process.argv.findIndex(
    (a) => a === `--${name}` || a.startsWith(`--${name}=`)
  );
  if (ix === -1) return undefined;
  const val = process.argv[ix].split("=")[1] ?? process.argv[ix + 1];
  return val;
}

function formatTimestamp(date) {
  const pad = (n) => n.toString().padStart(2, "0");
  const YYYY = date.getFullYear();
  const MM = pad(date.getMonth() + 1);
  const DD = pad(date.getDate());
  const hh = pad(date.getHours());
  const mm = pad(date.getMinutes());
  const ss = pad(date.getSeconds());
  return `${YYYY}${MM}${DD}_${hh}${mm}${ss}`;
}

const projectRoot = process.cwd();
const customLogsDir = getArg("logs-dir");
console.log(`customLogsDir: ${customLogsDir}`);

const logsDir = path.resolve(projectRoot, customLogsDir ?? "logs");
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

const customConfigPath = path.join(projectRoot, "build.customconfig.json");
let logFileName = "build.json"; // default filename

if (fs.existsSync(customConfigPath)) {
  try {
    const raw = fs.readFileSync(customConfigPath, "utf8");
    const customConfig = JSON.parse(raw);

    if (typeof customConfig.build_report_file === "string") {
      logFileName = customConfig.build_report_file;
      console.log(`Using custom log file: ${logFileName}`);
    } else {
      console.log(
        "Warning: 'build_report_file' is missing or not a string in build.customconfig.json"
      );
    }
  } catch (err) {
    console.log(
      `Warnig: Failed to read or parse build.customconfig.json: ${err.message}`
    );
  }
} else {
  console.log("No build.customconfig.json found. Using default build.json");
}

const logPath = path.join(logsDir, logFileName);

const records = [];
const summary = { errorCount: 0, warnCount: 0, infoCount: 0 };
const startTime = formatTimestamp(new Date());

const nextBin = path.join("node_modules", "next", "dist", "bin", "next");

const child = spawn(process.execPath, [nextBin, "build", "--turbopack"], {
  cwd: projectRoot,
  env: { ...process.env },
  stdio: ["ignore", "pipe", "pipe"],
  shell: true,
});

const levelOf = (msg, stream) => {
  const m = msg.toLowerCase();
  if (stream === "stderr") return "error";
  if (/\berror\b|^error\s[-:]/i.test(msg)) return "error";
  if (/\bwarn(ing)?\b/i.test(m)) return "warn";
  return "info";
};

const wire = (stream, name) => {
  const rl = readline.createInterface({ input: stream });
  rl.on("line", (line) => {
    const clean = stripAnsi(line ?? "");
    const level = levelOf(clean, name);
    if (level === "error") summary.errorCount += 1;
    else if (level === "warn") summary.warnCount += 1;
    else summary.infoCount += 1;
    records.push({ stream: name, message: clean });
    const prefix =
      level === "error" ? "[error]" : level === "warn" ? "[warn]" : "";
    process.stdout.write(prefix + clean + "\n");
  });
};

wire(child.stdout, "stdout");
wire(child.stderr, "stderr");

const t0 = Date.now();
child.on("close", (code) => {
  const endTime = formatTimestamp(new Date());
  const durationMs = Date.now() - t0;
  const result = {
    tool: "next-build",
    args: ["build", "--turbopack"],
    startTime,
    endTime,
    durationMs,
    exitCode: typeof code === "number" ? code : null,
    records,
    summary,
  };
  fs.writeFileSync(logPath, JSON.stringify(result, null, 2), "utf8");
  process.stdout.write(`Saved: ${logPath}\n`);
  process.exit(typeof code === "number" ? code : 1);
});
child.on("error", () => process.exit(1));
