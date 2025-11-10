import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";
import noImgElement from "./eslint-custom-rules/no-img-element.mjs";
import noTestidOnSelect from "./eslint-custom-rules/no-testid-on-select.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    ignores: [
      "node_modules/**",
      ".next/**",
      "out/**",
      "build/**",
      "next-env.d.ts",
    ],
    plugins: {
      "custom-rules": {
        rules: {
          "no-img-element": noImgElement,
          "no-testid-on-select": noTestidOnSelect,
        },
      },
    },
    rules: {
      "@next/next/no-img-element": "off",
      "custom-rules/no-img-element": "error",
      "custom-rules/no-testid-on-select": "error",
    },
  },
];

export default eslintConfig;
