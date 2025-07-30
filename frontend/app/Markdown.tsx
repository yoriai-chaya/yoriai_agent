"use client";

import React from "react";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";

type Props = { markdown: string };

type Token =
  | { type: "heading"; level: number; content: string }
  | { type: "code"; content: string; lang?: string }
  | { type: "ul"; items: string[] }
  | { type: "ol"; items: string[] }
  | { type: "p"; content: string };

const Markdown: React.FC<Props> = ({ markdown }) => {
  const tokens = React.useMemo(() => {
    const lines = markdown.split("\n");
    const tokens: Token[] = [];

    let codeMode = false;
    let codeLang = "";
    let codeBuffer: string[] = [];

    let listBuffer: string[] = [];
    let listType: "ul" | "ol" | null = null;

    for (let line of lines) {
      line = line.trimEnd();

      // start or end of a code block
      if (line.startsWith("```")) {
        if (!codeMode) {
          codeMode = true;
          codeLang = line.slice(3).trim();
          codeBuffer = [];
        } else {
          codeMode = false;
          tokens.push({
            type: "code",
            content: codeBuffer.join("\n"),
            lang: codeLang,
          });
        }
        continue;
      }

      if (codeMode) {
        codeBuffer.push(line);
        continue;
      }

      // heading(h1, h2, h3) (#, ##, ###)
      const headingMatch = line.match(/^(#{1,3})\s+(.*)/);
      if (headingMatch) {
        const level = headingMatch[1].length;
        const content = headingMatch[2];
        tokens.push({ type: "heading", level, content });
        continue;
      }

      // ol: ordered list (1. item)
      if (/^\d+\.\s+/.test(line)) {
        const item = line.replace(/^\d+\.\s+/, "");
        if (listType === "ol" || listType === null) {
          listType = "ol";
          listBuffer.push(item);
        } else {
          // previous <ui> is not closed
          tokens.push({ type: listType, items: listBuffer });
          listBuffer = [item];
          listType = "ol";
        }
        continue;
      }

      // unordered list (- item / * item)
      if (/^[-*]\s+/.test(line)) {
        const item = line.replace(/^[-*]\s+/, "");
        if (listType === "ul" || listType === null) {
          listType = "ul";
          listBuffer.push(item);
        } else {
          // previous <ol> is not closed
          tokens.push({ type: listType, items: listBuffer });
          listBuffer = [item];
          listType = "ul";
        }
        continue;
      }

      // empty line -> end of list
      if (line.trim() === "" && listType) {
        tokens.push({ type: listType, items: listBuffer });
        listBuffer = [];
        listType = null;
        continue;
      }

      // paragraph
      tokens.push({ type: "p", content: line });
    }

    // remaining lists or codes, add them to the end
    if (listType) {
      tokens.push({ type: listType, items: listBuffer });
    }
    if (codeMode && codeBuffer.length > 0) {
      tokens.push({
        type: "code",
        content: codeBuffer.join("\n"),
        lang: codeLang,
      });
    }

    return tokens;
  }, [markdown]);

  return (
    <ScrollArea className="max-h-[80vh] w-full space-y-4">
      {tokens.map((t, i) => {
        switch (t.type) {
          case "heading":
            const Tag = `h${t.level}` as keyof React.JSX.IntrinsicElements;
            const sizeClass =
              t.level === 1
                ? "text-[20px]"
                : t.level === 2
                ? "text-[18px]"
                : "text-[16px]";
            return (
              <Tag key={i} className={`${sizeClass} font-bold my-2`}>
                {t.content}
              </Tag>
            );
          case "code":
            return (
              <ScrollArea
                key={i}
                className="flex flex-nowrap overflow-x-auto bg-slate-800 rounded-sm text-slate-200"
              >
                <pre className="p-3 text-[10px]/3">
                  <div className="flex-none w-10">
                    <code>{t.content}</code>
                  </div>
                  <ScrollBar orientation="horizontal" />
                </pre>
              </ScrollArea>
            );
          case "ul":
            return (
              <ul
                key={i}
                className="list-disc pl-6 space-y-1 text-[14px]/4 my-2"
              >
                {t.items.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            );
          case "ol":
            return (
              <ol
                key={i}
                className="list-decimal pl-6 space-y-1 text-[14px]/4 my-2"
              >
                {t.items.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ol>
            );
          case "p":
            return (
              <p key={i} className="whitespace-pre-wrap text-[14px]">
                {t.content}
              </p>
            );
        }
      })}
      <ScrollBar orientation="horizontal" />
    </ScrollArea>
  );
};

export default Markdown;
