import { useCallback, useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Report } from "./types";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

function formatMoney(value: number) {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(value);
}

export default function App() {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadReport = useCallback(async () => {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams();
    if (startDate) params.set("start_date", startDate);
    if (endDate) params.set("end_date", endDate);
    const qs = params.toString();
    try {
      const res = await fetch(`${API_BASE}/api/report${qs ? `?${qs}` : ""}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setReport(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка загрузки");
      setReport(null);
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate]);

  useEffect(() => {
    loadReport();
  }, [loadReport]);

  const revenueChart = report?.revenue_by_doctor.map((r) => ({
    name: r.doctor_name.split(" ")[0],
    fullName: r.doctor_name,
    revenue: Number(r.revenue),
  }));

  const referralChart = report?.referral_by_doctor.map((r) => ({
    name: r.doctor_name.split(" ")[0],
    fullName: r.doctor_name,
    rate: Number(r.referral_rate_pct),
    referred: r.patients_referred,
    total: r.patients_first_visit,
  }));

  return (
    <div className="page">
      <header className="header">
        <div>
          <p className="eyebrow">ClinicIQ Analytics</p>
          <h1>Отчёт по врачам</h1>
          <p className="subtitle">
            Выручка и перенаправляемость пациентов (первый приём → приём у другого врача)
          </p>
        </div>
        <form
          className="filters"
          onSubmit={(e) => {
            e.preventDefault();
            loadReport();
          }}
        >
          <label>
            <span>С</span>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </label>
          <label>
            <span>По</span>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? "Загрузка…" : "Применить"}
          </button>
          <button
            type="button"
            className="ghost"
            onClick={() => {
              setStartDate("");
              setEndDate("");
            }}
          >
            Всё время
          </button>
        </form>
      </header>

      {error && <div className="error">{error}</div>}

      {report && (
        <>
          <section className="kpis">
            <article className="kpi">
              <span className="kpi-label">Общая выручка</span>
              <strong>{formatMoney(report.summary.total_revenue)}</strong>
            </article>
            <article className="kpi">
              <span className="kpi-label">Врачей в отчёте</span>
              <strong>{report.summary.doctors_count}</strong>
            </article>
            <article className="kpi">
              <span className="kpi-label">Средняя перенаправляемость</span>
              <strong>{report.summary.avg_referral_rate_pct}%</strong>
            </article>
          </section>

          <section className="charts">
            <div className="chart-card">
              <h2>Выручка по врачам</h2>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={revenueChart} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d3d52" />
                  <XAxis dataKey="name" tick={{ fill: "#8b9cb3", fontSize: 12 }} />
                  <YAxis tick={{ fill: "#8b9cb3", fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ background: "#1a2332", border: "1px solid #2d3d52" }}
                    formatter={(v: number) => [formatMoney(v), "Выручка"]}
                    labelFormatter={(_, payload) =>
                      payload?.[0]?.payload?.fullName ?? ""
                    }
                  />
                  <Bar dataKey="revenue" fill="#3d9cf5" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h2>Перенаправляемость, %</h2>
              <p className="chart-hint">
                Доля пациентов с первым приёмом у врача, которые позже посетили другого
              </p>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={referralChart} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d3d52" />
                  <XAxis dataKey="name" tick={{ fill: "#8b9cb3", fontSize: 12 }} />
                  <YAxis unit="%" tick={{ fill: "#8b9cb3", fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ background: "#1a2332", border: "1px solid #2d3d52" }}
                    formatter={(v: number) => [`${v}%`, "Перенаправляемость"]}
                    labelFormatter={(_, payload) =>
                      payload?.[0]?.payload?.fullName ?? ""
                    }
                  />
                  <Legend />
                  <Bar dataKey="rate" name="%" fill="#5dd9a8" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className="tables">
            <div className="table-card">
              <h2>Таблица выручки</h2>
              <table>
                <thead>
                  <tr>
                    <th>Врач</th>
                    <th>Выручка</th>
                    <th>Услуг</th>
                  </tr>
                </thead>
                <tbody>
                  {report.revenue_by_doctor.map((r) => (
                    <tr key={r.doctor_id}>
                      <td>{r.doctor_name}</td>
                      <td>{formatMoney(Number(r.revenue))}</td>
                      <td>{r.service_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="table-card">
              <h2>Таблица перенаправляемости</h2>
              <table>
                <thead>
                  <tr>
                    <th>Врач</th>
                    <th>Первичных пациентов</th>
                    <th>Перенаправлено</th>
                    <th>%</th>
                  </tr>
                </thead>
                <tbody>
                  {report.referral_by_doctor.map((r) => (
                    <tr key={r.doctor_id}>
                      <td>{r.doctor_name}</td>
                      <td>{r.patients_first_visit}</td>
                      <td>{r.patients_referred}</td>
                      <td>{r.referral_rate_pct}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <footer className="meta">
            Источник: {report.schema.visits_table} / {report.schema.revenue_table} · только чтение
          </footer>
        </>
      )}
    </div>
  );
}
