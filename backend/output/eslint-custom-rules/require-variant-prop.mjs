const requireVariantPropRule = {
  meta: {
    type: "problem",
    docs: {
      description:
        "Use boolean fill on <Image>: write <Image fill /> instead of <Image layout='fill' /> (deprecated).",
    },
    schema: [],
    messages: {
      missingProp: '{{tag}} components must have a "{{prop}}" prop.',
    },
  },
  create(context) {
    const requiredPropsMap = {
      Image: "fill",
    };

    return {
      JSXOpeningElement(node) {
        const tagName = node.name?.name;
        const requiredProp = requiredPropsMap[tagName];

        if (!requiredProp) return;

        const hasProp = node.attributes.some(
          (attr) =>
            attr.type === "JSXAttribute" && attr.name?.name === requiredProp
        );

        if (!hasProp) {
          context.report({
            node,
            messageId: "missingProp",
            data: {
              tag: tagName,
              prop: requiredProp,
            },
          });
        }
      },
    };
  },
};

export default requireVariantPropRule;
