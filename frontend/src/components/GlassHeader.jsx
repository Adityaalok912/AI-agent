import ThemeToggle from "./ThemeToggle";
import { useEffect, useState } from "react";

export default function GlassHeader({ project, duration }) {
  const [elapsed, setElapsed] = useState(duration);

  useEffect(() => {
    if (!project) return;
    const timer = setInterval(() => setElapsed((prev) => prev + 1), 1000);
    return () => clearInterval(timer);
  }, [project]);

  return (
    <header className="sticky top-0 z-30 backdrop-blur-lg bg-white/70 dark:bg-slate-900/60 border-b border-slate-200 dark:border-slate-700 shadow-sm rounded-xl mb-4">
      <div className="flex justify-between items-center px-6 py-4">
        <div>
          <h1 className="text-lg md:text-xl font-semibold text-slate-800 dark:text-slate-100">
            {project ? project.project_title : "🧠 Multi-Agent Dashboard"}
          </h1>
          {project && (
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Elapsed Time: {elapsed}s | Agents: {project.results?.length || "–"}
            </p>
          )}
        </div>
        <ThemeToggle />
      </div>
    </header>
  );
}
