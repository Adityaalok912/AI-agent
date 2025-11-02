import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { CheckCircle, Loader2, Maximize2, X } from "lucide-react";
import { motion } from "framer-motion";
import MarkdownMessage from "./MarkdownMessage";

const roleStyles = {
  Boss: "from-blue-500/20 to-blue-600/10",
  "Product Manager": "from-amber-500/20 to-amber-600/10",
  Architect: "from-emerald-500/20 to-emerald-600/10",
  Developer: "from-violet-500/20 to-violet-600/10",
  "Risk Agent": "from-rose-500/20 to-rose-600/10",
  default: "from-slate-400/20 to-slate-500/10",
};

const roleAvatars = {
  Boss: "🧑‍💼",
  "Product Manager": "📋",
  Architect: "🧱",
  Developer: "💻",
  "Risk Agent": "🕵️",
  default: "🤖",
};

export default function AgentOutputCard({
  agent,
  content,
  isActive,
  enableTyping = false, // keep your previous toggle; default off
  typeSpeed = 18,
}) {
  const avatar = roleAvatars[agent] || roleAvatars.default;
  const style = roleStyles[agent] || roleStyles.default;

  // Normalize content to a string
  const fullText = useMemo(() => {
    if (content == null) return "";
    return typeof content === "string" ? content : JSON.stringify(content, null, 2);
  }, [content]);

  // Typing effect state (optional)
  const [displayed, setDisplayed] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  // Fullscreen state
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Start/skip typing
  useEffect(() => {
    if (!fullText) {
      setDisplayed("");
      setIsTyping(false);
      return;
    }
    if (!enableTyping) {
      setDisplayed(fullText);
      setIsTyping(false);
      return;
    }
    setDisplayed("");
    setIsTyping(true);
    let i = 0;
    const timer = setInterval(() => {
      i++;
      setDisplayed(fullText.slice(0, i));
      if (i >= fullText.length) {
        clearInterval(timer);
        setIsTyping(false);
      }
    }, typeSpeed);
    return () => clearInterval(timer);
  }, [fullText, typeSpeed, enableTyping]);

  const showSpinner = isActive && !fullText;
  const showTyping = enableTyping && !showSpinner && (isTyping || (fullText && displayed !== fullText));
  const textToShow = enableTyping ? (showTyping ? displayed : fullText) : displayed || fullText;

  // Shared card body
  const CardBody = ({ padClass = "p-4", textSize = "text-sm" }) => (
    <motion.div
      className={`${padClass} rounded-xl shadow-md bg-gradient-to-br ${style} border border-slate-200 dark:border-slate-700 backdrop-blur-md`}
      // whileHover={{ scale: 1.02 }}
      layout
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{avatar}</span>
          <h4 className="font-semibold text-gray-900 dark:text-gray-100">{agent}</h4>
        </div>

        <div className="flex items-center gap-2">
          {showSpinner ? (
            <Loader2 className="animate-spin text-blue-500" size={20} />
          ) : (
            <CheckCircle
              className={showTyping ? "text-yellow-500" : "text-green-500"}
              size={20}
              title={showTyping ? "Typing…" : "Done"}
            />
          )}
          <button
            onClick={() => setIsFullscreen(true)}
            className="p-1.5 rounded hover:bg-white/20 dark:hover:bg-slate-700/50 transition-colors"
            title="Fullscreen"
            type="button"
          >
            <Maximize2 className="w-4 h-4 text-slate-700 dark:text-slate-200" />
          </button>
        </div>
      </div>

      <div className={`${textSize} text-gray-700 dark:text-gray-300 leading-relaxed mt-3 min-h-[2.5rem]`}>
        {showSpinner ? (
          <motion.div
            className="flex gap-1 mt-2"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ repeat: Infinity, duration: 1.2 }}
          >
            <span>●</span>
            <span>●</span>
            <span>●</span>
          </motion.div>
        ) : (
          <MarkdownMessage text={textToShow} />
        )}
      </div>
    </motion.div>
  );

  return (
    <>
      <CardBody />

      {isFullscreen &&
        createPortal(
          <div
            className="fixed inset-0 z-[100] bg-black/70 backdrop-blur-sm"
            onClick={(e) => {
              if (e.target === e.currentTarget) setIsFullscreen(false);
            }}
          >
            <button
              onClick={() => setIsFullscreen(false)}
              className="fixed top-4 right-4 z-[110] rounded-full p-2.5 bg-white/90 text-slate-900 hover:bg-white shadow-lg border border-black/10 dark:bg-slate-800/90 dark:text-white dark:hover:bg-slate-700"
              title="Close"
              aria-label="Close fullscreen"
              type="button"
            >
              <X className="w-5 h-5" />
            </button>
            <div className="h-full overflow-auto p-4">
              <div className="relative max-w-5xl mx-auto">
                <CardBody padClass="p-6" textSize="text-base" />
              </div>
            </div>
          </div>,
          document.body
        )}
    </>
  );
}