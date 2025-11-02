import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check } from "lucide-react";

// Renders inline and fenced code with a header and copy button for fenced blocks.
function CodeBlock({ inline, className, children, ...props }) {
  const [copied, setCopied] = useState(false);

  if (inline) {
    return (
      <code
        className="px-1.5 py-0.5 rounded bg-slate-200/70 dark:bg-slate-800/70 text-slate-900 dark:text-slate-100"
        {...props}
      >
        {children}
      </code>
    );
  }

  const match = /language-([a-z0-9+#-]+)/i.exec(className || "");
  const lang = match?.[1] || "text";
  const text = String(children).replace(/\n$/, "");

  const onCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    } catch (e) {
      console.error("Copy failed:", e);
    }
  };

  return (
    <div className="group not-prose relative rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 overflow-hidden">
      <div className="flex items-center justify-between px-3 py-2 text-xs bg-slate-100/70 dark:bg-slate-800/70 border-b border-slate-200 dark:border-slate-700">
        <span className="uppercase tracking-wide text-slate-600 dark:text-slate-300">{lang}</span>
        <button
          onClick={onCopy}
          className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-slate-700 dark:text-slate-200 hover:bg-white/80 dark:hover:bg-slate-700/60 transition-colors"
          title="Copy code"
          type="button"
        >
          {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
          <span className="text-xs">{copied ? "Copied" : "Copy"}</span>
        </button>
      </div>
      <pre className="m-0 p-3 overflow-x-auto text-sm leading-relaxed bg-slate-50 dark:bg-slate-900">
        <code className={className} {...props}>
          {text}
        </code>
      </pre>
    </div>
  );
}

export default function MarkdownMessage({ text }) {
  return (
    <div className="markdown-message text-gray-800 dark:text-gray-200">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Headings
          h1: (props) => <h1 className="text-2xl font-bold mt-4 mb-2" {...props} />,
          h2: (props) => <h2 className="text-xl font-semibold mt-4 mb-2" {...props} />,
          h3: (props) => <h3 className="text-lg font-semibold mt-3 mb-2" {...props} />,
          h4: (props) => <h4 className="text-base font-semibold mt-3 mb-1.5" {...props} />,
          // Text
          p: (props) => <p className="my-2 leading-relaxed" {...props} />,
          strong: (props) => <strong className="font-semibold" {...props} />,
          em: (props) => <em className="italic" {...props} />,
          // Lists
          ul: (props) => <ul className="list-disc ms-6 my-2 space-y-1" {...props} />,
          ol: (props) => <ol className="list-decimal ms-6 my-2 space-y-1" {...props} />,
          li: (props) => <li className="leading-relaxed" {...props} />,
          // Horizontal rule
          hr: (props) => <hr className="my-4 border-slate-300 dark:border-slate-700" {...props} />,
          // Links
          a: (props) => (
            <a
              className="text-violet-600 dark:text-violet-400 underline underline-offset-2 hover:opacity-90"
              target="_blank"
              rel="noopener noreferrer"
              {...props}
            />
          ),
          // Code
          code: CodeBlock,
        }}
      >
        {text || ""}
      </ReactMarkdown>
    </div>
  );
}