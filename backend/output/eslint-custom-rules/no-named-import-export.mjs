const ALLOWED_MODULE_PATTERNS = [
  /^react$/,
  /^react\/.+/,
  /^next\/.+/,
  /^lucide-react$/,
  /^@\/components\/ui\/.+/,
];

function isAllowedModule(source) {
  return ALLOWED_MODULE_PATTERNS.some((pattern) => pattern.test(source));
}

function isUserComponentImport(source) {
  // Relative paths are treated as user-defined components
  if (source.startsWith("./") || source.startsWith("../")) {
    return true;
  }

  // Treat "@/components/*" as user-defined components,
  // but exclude shared UI components under "@/components/ui"
  if (
    source.startsWith("@/components/") &&
    !source.startsWith("@/components/ui/")
  ) {
    return true;
  }

  return false;
}

const rule = {
  meta: {
    type: "problem",
    docs: {
      description: "Enforce default import/export for user-defined components.",
    },
    schema: [],
    messages: {
      noNamedImport:
        "User-defined components must be imported using default import.",
      noNamedExport:
        "User-defined components must be exported using default export.",
    },
  },

  create(context) {
    return {
      ImportDeclaration(node) {
        const source = node.source.value;

        // Skip allowed modules such as React, Next.js, and shared UI libraries
        if (isAllowedModule(source)) return;

        // Only check user-defined component imports
        if (!isUserComponentImport(source)) return;

        const hasNamedImport = node.specifiers.some(
          (spec) => spec.type === "ImportSpecifier"
        );

        if (hasNamedImport) {
          context.report({
            node,
            messageId: "noNamedImport",
          });
        }
      },

      ExportNamedDeclaration(node) {
        // re-export: export { Foo } from "./Foo"
        if (node.source) {
          const source = node.source.value;
          if (!isUserComponentImport(source)) return;
        }

        context.report({
          node,
          messageId: "noNamedExport",
        });
      },
    };
  },
};

export default rule;
