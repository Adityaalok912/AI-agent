import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LabelList,
} from "recharts";

export default function AgentMetricsChart({ metrics }) {
  if (!metrics || Object.keys(metrics).length === 0) return null;

  const data = Object.entries(metrics).map(([agent, m]) => ({
    name: agent,
    duration: Number(m.duration.toFixed(2)),
  }));

  return (
    <div className="rounded-xl bg-gradient-to-br from-white via-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900 shadow-inner border border-slate-200 dark:border-slate-700 p-5">
      <h3 className="font-semibold text-gray-800 dark:text-gray-100 mb-3">
        ⏱️ Agent Performance Overview
      </h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="name" tick={{ fill: "#475569" }} />
          <YAxis tick={{ fill: "#475569" }} unit="s" />
          <Tooltip contentStyle={{ backgroundColor: "#1e293b", color: "#f8fafc", borderRadius: "8px" }} />
          <Bar dataKey="duration" fill="url(#colorGradient)" radius={[6, 6, 0, 0]}>
            <LabelList dataKey="duration" position="top" fill="#0f172a" />
          </Bar>
          <defs>
            <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.9} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.8} />
            </linearGradient>
          </defs>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
