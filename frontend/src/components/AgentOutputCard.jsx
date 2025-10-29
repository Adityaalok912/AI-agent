import { CheckCircle, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

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

export default function AgentOutputCard({ agent, content, isActive }) {
  const avatar = roleAvatars[agent] || roleAvatars.default;
  const style = roleStyles[agent] || roleStyles.default;
  const isTyping = !content || isActive;

  return (
    <motion.div
      className={`p-4 rounded-xl shadow-md bg-gradient-to-br ${style} border border-slate-200 dark:border-slate-700 backdrop-blur-md`}
      whileHover={{ scale: 1.02 }}
      layout
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{avatar}</span>
          <h4 className="font-semibold text-gray-900 dark:text-gray-100">
            {agent}
          </h4>
        </div>
        {isTyping ? (
          <Loader2 className="animate-spin text-blue-500" size={20} />
        ) : (
          <CheckCircle className="text-green-500" size={20} />
        )}
      </div>

      <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed mt-2">
        {isTyping ? (
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
          content
        )}
      </div>
    </motion.div>
  );
}
