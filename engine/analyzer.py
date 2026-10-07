"""
FinPulse AI - Analytical Scoring Engine
Deterministic, mathematically sound financial health and credit readiness calculations.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np


class FinancialAnalyzer:
    """
    Computes deterministic financial indicators, debt sustainability ratios,
    volatility indices, and underwriting credit readiness scores for micro-enterprises.
    """

    EXPECTED_COLUMNS = [
        "Date", "Transaction_Type", "Category", "Amount", "Payment_Mode", "Description"
    ]

    def __init__(self, df: pd.DataFrame):
        self.raw_df = df.copy()
        self.df = self._clean_and_prepare_df(df)

    def _clean_and_prepare_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardizes and cleans input ledger dataframe."""
        data = df.copy()
        
        # Ensure standard column mapping if casing differs
        col_map = {c.strip().lower(): c for c in data.columns}
        for exp in self.EXPECTED_COLUMNS:
            exp_lower = exp.lower()
            if exp_lower in col_map and col_map[exp_lower] != exp:
                data.rename(columns={col_map[exp_lower]: exp}, inplace=True)
                
        # Fill missing values
        if "Date" in data.columns:
            data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
            data = data.dropna(subset=["Date"])
            data.sort_values("Date", inplace=True)
            
        if "Amount" in data.columns:
            data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce").fillna(0.0)
            data["Amount"] = data["Amount"].abs()
            
        if "Transaction_Type" in data.columns:
            data["Transaction_Type"] = data["Transaction_Type"].astype(str).str.strip().str.upper()
            
        if "Category" in data.columns:
            data["Category"] = data["Category"].astype(str).str.strip()
            
        if "Payment_Mode" in data.columns:
            data["Payment_Mode"] = data["Payment_Mode"].astype(str).str.strip()

        # Add signed amount column (+ for CREDIT, - for DEBIT)
        data["Signed_Amount"] = np.where(
            data["Transaction_Type"] == "CREDIT",
            data["Amount"],
            -data["Amount"]
        )
        return data

    def compute_kpis(self) -> Dict[str, Any]:
        """Computes executive high-level summary KPIs."""
        credits_df = self.df[self.df["Transaction_Type"] == "CREDIT"]
        debits_df = self.df[self.df["Transaction_Type"] == "DEBIT"]

        total_inflow = float(credits_df["Amount"].sum())
        total_outflow = float(debits_df["Amount"].sum())
        net_cash_flow = total_inflow - total_outflow

        # Date range & duration
        if not self.df.empty and "Date" in self.df.columns:
            start_date = self.df["Date"].min()
            end_date = self.df["Date"].max()
            days_span = max((end_date - start_date).days + 1, 1)
        else:
            days_span = 1
            start_date = None
            end_date = None

        avg_daily_inflow = total_inflow / days_span
        avg_daily_burn = total_outflow / days_span

        # Net Profit Margin %
        net_margin_pct = (net_cash_flow / total_inflow * 100) if total_inflow > 0 else 0.0

        # Debt obligations
        debt_df = debits_df[debits_df["Category"].str.lower().str.contains("debt|loan|emi|interest", regex=True)]
        total_debt_service = float(debt_df["Amount"].sum())

        # Operating Outflows (excluding debt)
        operating_outflows = total_outflow - total_debt_service
        net_operating_income = total_inflow - operating_outflows

        # Debt Service Coverage Ratio (DSCR)
        # DSCR = Net Operating Income / Total Debt Service
        if total_debt_service > 0:
            dscr = net_operating_income / total_debt_service
        else:
            dscr = 999.0  # Zero debt burden

        # Working Capital Runway in Days
        # Cumulative reserve / Average daily burn rate
        # If cumulative net flow is positive, runway = net_cash_flow / daily_burn
        if avg_daily_burn > 0:
            runway_days = max(net_cash_flow, 0) / avg_daily_burn
        else:
            runway_days = 999.0

        # Cash Flow Volatility Index (CV = std / mean of weekly net flows)
        weekly_cv, weekly_summary = self._compute_weekly_volatility()

        # Digital Penetration Ratio
        digital_modes = ["UPI", "BANK TRANSFER", "NET BANKING", "CARD", "IMPS", "NEFT", "RTGS"]
        digital_credits = credits_df[credits_df["Payment_Mode"].str.upper().isin(digital_modes)]["Amount"].sum()
        digital_ratio = (digital_credits / total_inflow * 100) if total_inflow > 0 else 0.0

        # Composite Credit Score
        score_breakdown = self._compute_credit_score(
            volatility_cv=weekly_cv,
            net_margin_pct=net_margin_pct,
            dscr=dscr,
            debt_ratio=(total_debt_service / total_inflow * 100) if total_inflow > 0 else 0.0,
            digital_ratio=digital_ratio,
            runway_days=runway_days
        )

        return {
            "total_inflow": total_inflow,
            "total_outflow": total_outflow,
            "net_cash_flow": net_cash_flow,
            "days_span": days_span,
            "start_date": start_date,
            "end_date": end_date,
            "avg_daily_inflow": avg_daily_inflow,
            "avg_daily_burn": avg_daily_burn,
            "net_margin_pct": net_margin_pct,
            "total_debt_service": total_debt_service,
            "operating_outflows": operating_outflows,
            "net_operating_income": net_operating_income,
            "dscr": dscr,
            "runway_days": runway_days,
            "weekly_cv": weekly_cv,
            "weekly_summary": weekly_summary,
            "digital_ratio": digital_ratio,
            "score_breakdown": score_breakdown,
            "transaction_count": len(self.df)
        }

    def _compute_weekly_volatility(self) -> Tuple[float, pd.DataFrame]:
        """Aggregates weekly cash inflows, outflows and net flows, then computes CV."""
        if self.df.empty:
            return 0.0, pd.DataFrame()

        df_time = self.df.set_index("Date").copy()
        
        # Resample to weekly
        credits_w = df_time[df_time["Transaction_Type"] == "CREDIT"]["Amount"].resample("W-MON").sum()
        debits_w = df_time[df_time["Transaction_Type"] == "DEBIT"]["Amount"].resample("W-MON").sum()
        
        weekly = pd.DataFrame({
            "Inflow": credits_w,
            "Outflow": debits_w
        }).fillna(0.0)
        weekly["Net"] = weekly["Inflow"] - weekly["Outflow"]
        weekly["Cumulative_Balance"] = weekly["Net"].cumsum()

        # Coefficient of variation on weekly inflows and net flows
        mean_net = weekly["Net"].mean()
        std_net = weekly["Net"].std(ddof=1) if len(weekly) > 1 else 0.0

        if abs(mean_net) > 1e-6:
            # Coefficient of Variation CV = std / mean
            cv = float(abs(std_net / mean_net))
        else:
            cv = 1.0

        return cv, weekly.reset_index()

    def _compute_credit_score(
        self,
        volatility_cv: float,
        net_margin_pct: float,
        dscr: float,
        debt_ratio: float,
        digital_ratio: float,
        runway_days: float
    ) -> Dict[str, Any]:
        """
        4-Pillar Credit Readiness Composite Scoring Model (0-100 scale).
        Pillars:
        1. Cash Flow Stability (30% weight)
        2. Margin Adequacy & Surplus (25% weight)
        3. Debt Burden & Repayment Discipline (25% weight)
        4. Digital Record Verifiability (20% weight)
        """
        # Pillar 1: Cash Flow Stability (Max 30 pts)
        # Low CV (< 0.5) is excellent, > 1.5 is volatile
        if volatility_cv <= 0.35:
            stability_sub = 30.0
        elif volatility_cv <= 0.70:
            stability_sub = 25.0
        elif volatility_cv <= 1.10:
            stability_sub = 18.0
        elif volatility_cv <= 1.60:
            stability_sub = 10.0
        else:
            stability_sub = 5.0

        # Adjust for runway buffer
        if runway_days >= 30:
            stability_sub = min(30.0, stability_sub + 2.0)
        elif runway_days < 10:
            stability_sub = max(0.0, stability_sub - 4.0)

        # Pillar 2: Margin Adequacy & Net Surplus (Max 25 pts)
        # Healthy margin is > 15-20%
        if net_margin_pct >= 25.0:
            margin_sub = 25.0
        elif net_margin_pct >= 15.0:
            margin_sub = 21.0
        elif net_margin_pct >= 8.0:
            margin_sub = 16.0
        elif net_margin_pct >= 2.0:
            margin_sub = 10.0
        elif net_margin_pct >= 0.0:
            margin_sub = 5.0
        else:
            margin_sub = 0.0  # Cash burning / negative margin

        # Pillar 3: Debt Burden & Repayment Discipline (Max 25 pts)
        # DSCR >= 1.5 is standard institutional micro-lending benchmark
        if dscr >= 990:  # Zero existing debt
            debt_sub = 23.0  # Healthy, slight penalty for lack of borrowing track record
        elif dscr >= 2.0:
            debt_sub = 25.0
        elif dscr >= 1.4:
            debt_sub = 20.0
        elif dscr >= 1.0:
            debt_sub = 13.0
        elif dscr >= 0.7:
            debt_sub = 6.0
        else:
            debt_sub = 0.0  # Insolvent / incapable of servicing existing debt

        # Check debt-to-inflow percentage
        if debt_ratio > 35.0:
            debt_sub = max(0.0, debt_sub - 5.0)

        # Pillar 4: Digital Record Verifiability (Max 20 pts)
        # High digital penetration (> 75%) provides audit trail on UPI/Bank statements
        if digital_ratio >= 80.0:
            digital_sub = 20.0
        elif digital_ratio >= 60.0:
            digital_sub = 16.0
        elif digital_ratio >= 40.0:
            digital_sub = 11.0
        elif digital_ratio >= 20.0:
            digital_sub = 6.0
        else:
            digital_sub = 2.0

        composite_score = round(stability_sub + margin_sub + debt_sub + digital_sub, 1)
        composite_score = max(0.0, min(100.0, composite_score))

        # Risk Classification Badge
        if composite_score >= 75.0:
            risk_tier = "Prime Credit Readiness"
            risk_color = "emerald"
            badge_class = "success"
        elif composite_score >= 50.0:
            risk_tier = "Moderate Risk / Conditional"
            risk_color = "amber"
            badge_class = "warning"
        else:
            risk_tier = "High Risk / Sub-Prime"
            risk_color = "rose"
            badge_class = "danger"

        return {
            "composite_score": composite_score,
            "risk_tier": risk_tier,
            "risk_color": risk_color,
            "badge_class": badge_class,
            "pillars": {
                "Cash Flow Stability": {
                    "score": round(stability_sub, 1),
                    "max": 30.0,
                    "pct": round(stability_sub / 30.0 * 100, 1)
                },
                "Margin Adequacy": {
                    "score": round(margin_sub, 1),
                    "max": 25.0,
                    "pct": round(margin_sub / 25.0 * 100, 1)
                },
                "Debt Repayment Discipline": {
                    "score": round(debt_sub, 1),
                    "max": 25.0,
                    "pct": round(debt_sub / 25.0 * 100, 1)
                },
                "Digital Record Verifiability": {
                    "score": round(digital_sub, 1),
                    "max": 20.0,
                    "pct": round(digital_sub / 20.0 * 100, 1)
                }
            }
        }

    def generate_underwriting_audit(self, kpis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identifies red flags, strengths, and gives targeted recommendations
        aligned with micro-credit policies (MUDRA, PM SVANidhi, NBFC standards).
        """
        red_flags: List[Dict[str, str]] = []
        strengths: List[Dict[str, str]] = []
        recommendations: List[Dict[str, str]] = []

        dscr = kpis["dscr"]
        net_margin = kpis["net_margin_pct"]
        volatility_cv = kpis["weekly_cv"]
        runway_days = kpis["runway_days"]
        digital_ratio = kpis["digital_ratio"]
        total_debt = kpis["total_debt_service"]
        total_inflow = kpis["total_inflow"]

        debt_ratio = (total_debt / total_inflow * 100) if total_inflow > 0 else 0

        # Red Flag Checks
        if dscr < 1.0 and total_debt > 0:
            red_flags.append({
                "severity": "CRITICAL",
                "title": f"Inadequate Debt Service Coverage (DSCR: {dscr:.2f}x)",
                "description": f"Net operating surplus is insufficient to service current debt obligations (benchmark is >= 1.25x). Extreme default risk for additional leverage."
            })
        elif dscr < 1.3 and total_debt > 0:
            red_flags.append({
                "severity": "WARNING",
                "title": f"Tight Debt Service Cushion (DSCR: {dscr:.2f}x)",
                "description": f"Coverage is below recommended institutional tolerance of 1.5x. Any adverse shock to weekly revenue could impair debt service."
            })

        if debt_ratio > 30.0:
            red_flags.append({
                "severity": "HIGH",
                "title": f"Excessive Debt-to-Revenue Ratio ({debt_ratio:.1f}%)",
                "description": f"More than 30% of gross inflows are dedicated to debt repayment, severely starving operational working capital."
            })

        if net_margin < 0:
            red_flags.append({
                "severity": "CRITICAL",
                "title": f"Negative Operating Margin ({net_margin:.1f}%)",
                "description": "Enterprise is currently burning capital on a cash basis. Operating expenditures exceed top-line collections."
            })
        elif net_margin < 5.0:
            red_flags.append({
                "severity": "WARNING",
                "title": f"Thin Margin Vulnerability ({net_margin:.1f}%)",
                "description": "Net surplus margin is under 5%. Thin margin leaves zero safety buffer for inflation or supplier price spikes."
            })

        if volatility_cv > 1.2:
            red_flags.append({
                "severity": "HIGH",
                "title": f"Severe Cash Flow Volatility (CV: {volatility_cv:.2f})",
                "description": "Weekly net inflows exhibit high dispersion. Weekly fluctuations increase likelihood of missed loan installments."
            })

        if runway_days < 10:
            red_flags.append({
                "severity": "HIGH",
                "title": f"Critical Working Capital Runway ({runway_days:.1f} Days)",
                "description": f"Enterprise has less than 10 days of cash reserves at current daily burn rate ({kpis['avg_daily_burn']:,.0f} INR/day)."
            })

        if digital_ratio < 35.0:
            red_flags.append({
                "severity": "MEDIUM",
                "title": f"Opaque Cash Reliance ({100 - digital_ratio:.1f}% Cash)",
                "description": "High reliance on physical cash transactions prevents automated bank statement underwriting and reduces credit scoring confidence."
            })

        # Strengths Identification
        if digital_ratio >= 75.0:
            strengths.append({
                "title": f"Robust Digital Footprint ({digital_ratio:.1f}% UPI/Bank)",
                "description": "Verifiable transaction trail on digital payment rails enables quick automated bank statement underwriting."
            })

        if dscr >= 1.75 or total_debt == 0:
            dscr_text = f"{dscr:.2f}x" if total_debt > 0 else "Debt-Free"
            strengths.append({
                "title": f"Comfortable Debt Servicing Capacity ({dscr_text})",
                "description": "Substantial surplus cushion guarantees uninterrupted debt repayment even during transient downturns."
            })

        if volatility_cv <= 0.6:
            strengths.append({
                "title": f"Highly Predictable Cash Cadence (CV: {volatility_cv:.2f})",
                "description": "Weekly net inflows demonstrate steady, predictable customer demand and disciplined inventory purchases."
            })

        if runway_days >= 30:
            strengths.append({
                "title": f"Healthy Liquidity Buffer ({runway_days:.0f} Days Runway)",
                "description": "Enterprise maintains over a month of operational working capital reserves."
            })

        # Actionable Recommendations & Loan Scheme Alignment
        if digital_ratio < 60.0:
            recommendations.append({
                "pillar": "Digital Record Verifiability",
                "action": "Incentivize UPI QR code payments for customers and pay wholesale vendors via IMPS/UPI to establish formal verifiable bank velocity."
            })

        if runway_days < 20:
            recommendations.append({
                "pillar": "Working Capital",
                "action": "Negotiate 14-day vendor credit cycles and establish a dedicated contingency reserve account equal to at least 21 days of operational expenses."
            })

        if dscr < 1.4 and total_debt > 0:
            recommendations.append({
                "pillar": "Debt Restructuring",
                "action": "Refinance high-cost informal moneylender debt into longer-tenor institutional micro-credit (e.g. MUDRA Shishu/Kishore scheme) to lower monthly EMI burden."
            })

        if kpis["score_breakdown"]["composite_score"] >= 70:
            recommendations.append({
                "pillar": "Financing Pathway",
                "action": "Eligible for formal banking credit: Recommend applying for PM MUDRA (Kishore ₹50,000 - ₹5 Lakhs) or collateral-free CGTMSE small business credit lines."
            })
        elif kpis["score_breakdown"]["composite_score"] >= 50:
            recommendations.append({
                "pillar": "Financing Pathway",
                "action": "Prime candidate for PM SVANidhi (₹10,000 - ₹50,000 micro-credit with 7% interest subsidy) or MUDRA Shishu loan up to ₹50,000 with UPI turnover proof."
            })
        else:
            recommendations.append({
                "pillar": "Financing Pathway",
                "action": "Focus on 60-day ledger hygiene: eliminate discretionary expenses, maintain steady UPI receipts, and build 15 days of cash buffer before applying for credit."
            })

        return {
            "red_flags": red_flags,
            "strengths": strengths,
            "recommendations": recommendations
        }
