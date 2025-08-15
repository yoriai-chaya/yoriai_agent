import pluginReact from 'eslint-plugin-react';
import parser from '@typescript-eslint/parser';
import pluginTs from '@typescript-eslint/eslint-plugin';
import requireVariantProp from './eslint-custom-rules/require-variant-prop.js';

/** @type {import("eslint").Linter.FlatConfig[]} */
export default [
  {
    ignores: ['.next/**/*', 'next.config.ts'],
  },
  {
    files: ['app/*.ts', 'app/*.tsx'],
    languageOptions: {
      parser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: { jsx: true },
        project: './tsconfig.json', // 必要に応じて
      },
    },
    plugins: {
      '@typescript-eslint': pluginTs,
      react: pluginReact,
      'custom-rules': {
        rules: {
          'require-variant-prop': requireVariantProp,
        },
      },
    },
    rules: {
      // TypeScript用ルール（例）
      '@typescript-eslint/no-unused-vars': 'warn',

      // React推奨ルール（必要に応じて追加）
      'react/jsx-uses-react': 'off',
      'react/react-in-jsx-scope': 'off',

      // カスタムルール適用
      'custom-rules/require-variant-prop': 'error',
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },
];

