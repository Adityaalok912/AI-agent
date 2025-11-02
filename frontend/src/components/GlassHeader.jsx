import { Github, CircleDot } from "lucide-react";
import ThemeToggle from "./ThemeToggle";

function formatTime(totalSeconds = 0) {
  const s = Math.max(0, Math.floor(totalSeconds));
  const hrs = Math.floor(s / 3600);
  const mins = Math.floor((s % 3600) / 60);
  const secs = s % 60;
  const pad = (n) => String(n).padStart(2, "0");
  return hrs > 0 ? `${pad(hrs)}:${pad(mins)}:${pad(secs)}` : `${pad(mins)}:${pad(secs)}`;
}

export default function GlassHeader({ project, isRunning = false, elapsedSeconds = 0 }) {
  const repoUrl = "https://github.com/Adityaalok912/AI-agent";

  return (
    <header className="sticky top-0 z-20 bg-slate-100/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-700 shadow-lg">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex justify-between items-center h-16">
          <div className="flex-shrink-0">
            <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
              {project?.project_title || "AutoTeamAI Dashboard"}
            </h1>
            {project?.project_title && (
              <p className="text-xs text-slate-600 dark:text-slate-400">
                Project ID: {project.project_id}
              </p>
            )}
          </div>

          <div className="flex items-center gap-3">
            {/* Stopwatch pill */}
            <div
              className={[
                "flex items-center gap-2 rounded-full border px-3 py-1.5 font-mono text-sm",
                "border-slate-300 text-slate-800 bg-white/70",
                "dark:border-slate-600 dark:text-slate-100 dark:bg-slate-800/70",
              ].join(" ")}
              aria-live="polite"
              title={isRunning ? "Workflow running" : "Workflow stopped"}
            >
              <CircleDot
                className={isRunning ? "text-emerald-500 animate-pulse" : "text-slate-400"}
                size={14}
                aria-hidden
              />
              <span>{formatTime(elapsedSeconds)}</span>
            </div>

            <ThemeToggle />
            <a
              href={repoUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-600 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white transition-colors"
              aria-label="GitHub Repository"
            >
              <Github className="w-6 h-6" />
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}