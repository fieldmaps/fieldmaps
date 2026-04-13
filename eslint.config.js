import tsPlugin from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";
import eslintConfigPrettier from "eslint-config-prettier";

export default [
  {
    files: ["**/*.ts"],
    plugins: {
      "@typescript-eslint": tsPlugin,
    },
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        sourceType: "module",
        ecmaVersion: 2020,
      },
      globals: {
        browser: true,
        node: true,
      },
    },
    rules: {
      ...tsPlugin.configs.recommended.rules,
      "func-style": ["error", "declaration"],
    },
  },
  eslintConfigPrettier,
  {
    ignores: ["dist/", "node_modules/", ".astro/"],
  },
];
