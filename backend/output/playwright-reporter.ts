import type {
  FullConfig,
  FullResult,
  Reporter,
  Suite,
  TestCase,
  TestError,
  TestResult,
} from "@playwright/test/reporter";
import fs from "node:fs";

type FieldDef = {
  key: string;
  pattern: RegExp;
  stripQuotes?: boolean;
};
const stripAnsi = (s: string) => s.replace(/\u001b\[[0-9;]*m/g, "");
const unquote = (s: string) => s.trim().replace(/^"([\s\S]*)"$/, "$1");

const DEFAULT_FIELD_DEFS: FieldDef[] = [
  { key: "Error", pattern: /^Error:\s*(.+)$/m },
  { key: "Locator", pattern: /^Locator:\s*(.+)$/m },
  {
    key: "Expected string",
    pattern: /^Expected (?:string|value|pattern):\s*(.+)$/m,
    stripQuotes: true,
  },
  {
    key: "Received string",
    pattern: /^Received (?:string|value):\s*(.+)$/m,
    stripQuotes: true,
  },
  {
    key: "Expected",
    pattern: /^Expected:\s*([\s\S]*?)(?=^Received:|\Z)/m,
    stripQuotes: true,
  },
  {
    key: "Received",
    pattern: /^Received:\s*([^\n]*)/m,
    stripQuotes: true,
  },
];

type JsonRow = {
  title: string;
  status: TestResult["status"];
  location: TestCase["location"];
  errors: Record<string, string>[];
};
class CustomReporter implements Reporter {
  private results: JsonRow[] = [];
  private outputFile = "results/playwright_result.json";
  private fieldDefs: FieldDef[] = DEFAULT_FIELD_DEFS;

  onBegin(config: FullConfig, suite: Suite) {
    console.log(`----- Starting the run with ${suite.allTests().length} tests -----`);
    console.log("suite");
    console.log(suite);
  }

  onTestBegin(test: TestCase) {
    console.log(`----- Starting test: ${test.title} -----`);
    console.log("test");
    console.log(test);
  }

  private parseError(err: TestError) {
    const raw0 = err.message ?? err.value ?? "";
    const raw = stripAnsi(raw0).replace(/\r/g, "");

    const trimmed = raw.split(/\n+Call log:\n/)[0];

    const out: Record<string, string> = {};
    for (const def of this.fieldDefs) {
      const m = trimmed.match(def.pattern);
      if (m && m[1] != null) {
        const v = def.stripQuotes ? unquote(m[1]) : m[1].trim();
        out[def.key] = v;
      }
    }
    return out;
  }
  onTestEnd(test: TestCase, result: TestResult): void {
    console.log(`----- Finished test: ${test.title} -----`);
    console.log("test");
    console.log(test);
    console.log("result");
    console.log(result);

    const parseErrors = (result.errors ?? []).map((e) => this.parseError(e));

    this.results.push({
      title: test.title,
      status: result.status,
      location: test.location,
      errors: parseErrors,
    });
  }

  onEnd(result: FullResult) {
    console.log(`----- Finished the run: ${result.status} -----`);
    console.log("result");
    console.log(result);
    fs.writeFileSync(
      this.outputFile,
      JSON.stringify({ results: this.results }, null, 2),
      "utf8"
    );
  }
}

export default CustomReporter;
