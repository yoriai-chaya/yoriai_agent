export default {
  meta: {
    type: "problem",
    docs: {
      description:
        "If the <Image> component doesn't have a size yet, add the fill property.",
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
