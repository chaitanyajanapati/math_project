import { useEffect, useMemo, useState } from "react";
import { fetchQualitySummary, fetchQualityPerQuestion } from "../services/api";
import type { QualityQuestionItem, QualitySummary } from "../services/api";
import { BarChart3, CheckCircle2, AlertTriangle, Scale, ListChecks, Info } from "lucide-react";

function PercentBadge({ value }: { value: number }) {
  const pct = Math.round((value || 0) * 100);
  const color = pct >= 80 ? "bg-green-100 text-green-700 border-green-300" : pct >= 60 ? "bg-yellow-100 text-yellow-700 border-yellow-300" : "bg-red-100 text-red-700 border-red-300";
  return (
    <span className={`px-2 py-0.5 rounded-md text-sm font-semibold border ${color}`}>{pct}%</span>
  );
}

function TinyBar({ value, label, color }: { value: number; label: string; color: string }) {
  const width = Math.min(100, Math.max(0, value));
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs text-gray-600">
        <span>{label}</span>
        <span>{Math.round(width)}%</span>
      </div>
      <div className="h-2 rounded-full bg-gray-200 overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all duration-700 ease-out`} style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}

export default function QuestionQualityDashboard() {
  const [mounted, setMounted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<QualitySummary | null>(null);
  const [rows, setRows] = useState<QualityQuestionItem[]>([]);

  useEffect(() => {
    setMounted(true);
    (async () => {
      try {
        const [s, q] = await Promise.all([fetchQualitySummary().catch(() => null as unknown as QualitySummary), fetchQualityPerQuestion().catch(() => [] as QualityQuestionItem[])]);
        setSummary(s);
        setRows(q);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const levelPercents = useMemo(() => {
    const levels = summary?.complexity.by_level || {};
    const total = Object.values(levels).reduce((a, b) => a + b, 0) || 1;
    return Object.entries(levels).map(([k, v]) => ({ level: k, pct: (v / total) * 100 }));
  }, [summary]);

  return (
    <div className="min-h-[calc(100vh-64px)] bg-linear-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className={`flex items-center gap-3 mb-6 transition-all duration-500 ${mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"}`}>
          <BarChart3 className="w-8 h-8 text-indigo-600" />
          <h1 className="text-3xl font-bold text-indigo-800">Question Quality</h1>
        </div>

        {/* Loading skeleton */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-28 rounded-xl bg-white border-2 border-indigo-200 shadow-sm overflow-hidden">
                <div className="h-full animate-pulse bg-linear-to-r from-indigo-50 via-white to-indigo-50" />
              </div>
            ))}
          </div>
        )}

        {/* Summary cards */}
        {!loading && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="group bg-white rounded-xl border-2 border-indigo-200 shadow-sm p-5 hover:shadow-md transition-all hover:-translate-y-0.5">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 text-indigo-700 font-semibold"><CheckCircle2 className="w-5 h-5" /> Overall Quality</div>
                <PercentBadge value={summary?.quality.overall || 0} />
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm text-gray-700">
                <div className="flex items-center gap-1" title="Clarity"><Info className="w-4 h-4 text-indigo-500" /> Clarity</div>
                <PercentBadge value={summary?.quality.clarity || 0} />
                <div className="flex items-center gap-1" title="Difficulty Calibration"><Scale className="w-4 h-4 text-indigo-500" /> Calibration</div>
                <PercentBadge value={summary?.quality.difficulty_calibration || 0} />
              </div>
            </div>

            <div className="group bg-white rounded-xl border-2 border-blue-200 shadow-sm p-5 hover:shadow-md transition-all hover:-translate-y-0.5">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 text-blue-700 font-semibold"><ListChecks className="w-5 h-5" /> Total Questions</div>
                <span className="text-2xl font-bold text-blue-700">{summary?.counts.total || 0}</span>
              </div>
              <div className="text-xs text-gray-600">Across topics: {Object.keys(summary?.counts.by_topic || {}).length}</div>
            </div>

            <div className="group bg-white rounded-xl border-2 border-amber-200 shadow-sm p-5 hover:shadow-md transition-all hover:-translate-y-0.5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 text-amber-700 font-semibold"><AlertTriangle className="w-5 h-5" /> Top Issues</div>
              </div>
              <ul className="space-y-1 text-sm text-gray-700">
                {(summary?.issues.top || []).slice(0, 3).map((it) => (
                  <li key={it.issue} className="flex items-center justify-between">
                    <span className="truncate mr-2" title={it.issue}>{it.issue.replaceAll('_', ' ')}</span>
                    <span className="text-xs bg-amber-100 text-amber-700 border border-amber-300 rounded px-2 py-0.5">{it.count}</span>
                  </li>
                ))}
                {(!summary || (summary.issues.top || []).length === 0) && <li className="text-gray-500">No issues yet</li>}
              </ul>
            </div>
          </div>
        )}

        {/* Complexity distribution */}
        {!loading && (
          <div className="bg-white rounded-xl border-2 border-purple-200 shadow-sm p-5 mb-6">
            <div className="flex items-center gap-2 mb-4 text-purple-700 font-semibold"><BarChart3 className="w-5 h-5" /> Complexity Distribution</div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {levelPercents.length > 0 ? (
                levelPercents.map((x) => (
                  <TinyBar key={x.level} value={x.pct} label={x.level.replaceAll('_', ' ')} color="bg-gradient-to-r from-purple-500 to-fuchsia-500" />
                ))
              ) : (
                <div className="text-gray-500">No data yet</div>
              )}
            </div>
          </div>
        )}

        {/* Samples table */}
        {!loading && (
          <div className="bg-white rounded-xl border-2 border-gray-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <div className="font-semibold text-gray-800">Recent Questions</div>
              <div className="text-xs text-gray-500">Hover rows for details</div>
            </div>
            <div className="max-h-[420px] overflow-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 sticky top-0 z-10">
                  <tr>
                    <th className="text-left p-3 font-semibold text-gray-700">Question</th>
                    <th className="text-left p-3 font-semibold text-gray-700">Topic</th>
                    <th className="text-left p-3 font-semibold text-gray-700">Grade</th>
                    <th className="text-left p-3 font-semibold text-gray-700">Difficulty</th>
                    <th className="text-left p-3 font-semibold text-gray-700">Complexity</th>
                    <th className="text-left p-3 font-semibold text-gray-700">Quality</th>
                    <th className="text-left p-3 font-semibold text-gray-700">Issues</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.length > 0 ? (
                    rows.slice(0, 50).map((r) => (
                      <tr key={r.id} className="border-t border-gray-100 hover:bg-indigo-50/50 transition-colors">
                        <td className="p-3 max-w-[420px]">
                          <div className="line-clamp-2" title={r.question}>{r.question}</div>
                        </td>
                        <td className="p-3 capitalize">{r.topic.replaceAll('_', ' ')}</td>
                        <td className="p-3">{r.grade}</td>
                        <td className="p-3 capitalize">{r.difficulty}</td>
                        <td className="p-3">
                          <div className="flex items-center gap-2">
                            <span className="text-xs rounded px-2 py-0.5 border bg-purple-50 text-purple-700 border-purple-300">{r.complexity.level.replaceAll('_', ' ')}</span>
                            <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div className="h-full bg-linear-to-r from-purple-500 to-fuchsia-500" style={{ width: `${Math.min(100, r.complexity.normalized * 100)}%` }} />
                            </div>
                          </div>
                        </td>
                        <td className="p-3"><PercentBadge value={(r.quality.overall as number) || 0} /></td>
                        <td className="p-3 text-xs text-gray-600">
                          {r.issues.length ? (
                            <div className="flex gap-1 flex-wrap">
                              {r.issues.slice(0, 3).map((i) => (
                                <span key={i} className="px-2 py-0.5 rounded border bg-amber-50 text-amber-700 border-amber-300" title={i}>{i.replaceAll('_', ' ')}</span>
                              ))}
                              {r.issues.length > 3 && <span className="text-gray-500">+{r.issues.length - 3} more</span>}
                            </div>
                          ) : (
                            <span className="text-gray-400">—</span>
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td className="p-4 text-gray-500" colSpan={7}>No questions yet. Generate some questions first.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
