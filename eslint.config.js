// Shared ESLint flat config for every TypeScript package in the workspace.
import js from "@eslint/js";
import jsxA11y from "eslint-plugin-jsx-a11y-x";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: [
      "**/dist/**",
      "**/dist-ssr/**",
      "**/coverage/**",
      "**/node_modules/**",
      "packages/api-client/src/schema.d.ts",
      "apps/api/**",
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  {
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
      globals: { ...globals.browser, ...globals.node },
    },
    rules: {
      "@typescript-eslint/consistent-type-imports": ["error", { fixStyle: "inline-type-imports" }],
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "@typescript-eslint/restrict-template-expressions": ["error", { allowNumber: true }],
      "no-console": ["error", { allow: ["warn", "error", "info"] }],
    },
  },
  {
    files: ["apps/web/**/*.tsx", "apps/web/**/*.ts"],
    ...jsxA11y.configs.strict,
    plugins: {
      ...jsxA11y.configs.strict.plugins,
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...jsxA11y.configs.strict.rules,
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": ["error", { allowConstantExport: true }],
    },
  },
  {
    files: ["**/*.test.ts", "**/*.test.tsx", "**/test/**"],
    rules: {
      "@typescript-eslint/no-non-null-assertion": "off",
      "react-refresh/only-export-components": "off",
    },
  },
  {
    files: ["**/*.js", "**/*.mjs"],
    ...tseslint.configs.disableTypeChecked,
  },
);
