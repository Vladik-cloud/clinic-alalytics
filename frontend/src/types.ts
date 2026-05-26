export interface ReportSummary {
  total_revenue: number;
  doctors_count: number;
  avg_referral_rate_pct: number;
  period: { start: string | null; end: string | null };
}

export interface RevenueRow {
  doctor_id: number;
  doctor_name: string;
  revenue: number;
  service_count: number;
}

export interface ReferralRow {
  doctor_id: number;
  doctor_name: string;
  patients_first_visit: number;
  patients_referred: number;
  referral_rate_pct: number;
}

export interface Report {
  summary: ReportSummary;
  revenue_by_doctor: RevenueRow[];
  referral_by_doctor: ReferralRow[];
  schema: {
    doctors_table: string;
    visits_table: string;
    revenue_table: string;
  };
}
