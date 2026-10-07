"""
FinPulse AI: Micro-Enterprise Financial Health & Credit Readiness Engine
Main Executive Dashboard Application (Streamlit)
Designed for the IBM Bharat Cares Internship.
"""

import json
import io
import datetime
import pandas as pd
import streamlit as st

# Import FinPulse AI modules
from engine.analyzer import FinancialAnalyzer
from engine.generator import PersonaGenerator
from engine.visualizer import FinancialVisualizer


# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="FinPulse AI | Micro-Enterprise Credit Readiness",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# CUSTOM STYLING (Tailwind / Clean Modern UI aesthetic)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 12px;
    }
    .metric-title {
        color: #64748B;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #0F172A;
        font-size: 1.65rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .metric-sub {
        color: #94A3B8;
        font-size: 0.78rem;
        margin-top: 4px;
    }
    
    /* Risk Badges */
    .badge-prime {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-moderate {
        background-color: #FFFBEB;
        color: #92400E;
        border: 1px solid #FDE68A;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-danger {
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }

    /* Red Flag & Audit Card */
    .audit-card {
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
        border-left: 4px solid;
    }
    .audit-critical {
        background-color: #FEF2F2;
        border-color: #EF4444;
        color: #7F1D1D;
    }
    .audit-warning {
        background-color: #FFFBEB;
        border-color: #F59E0B;
        color: #78350F;
    }
    .audit-success {
        background-color: #ECFDF5;
        border-color: #10B981;
        color: #064E3B;
    }
    .audit-info {
        background-color: #EFF6FF;
        border-color: #3B82F6;
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SIDEBAR - DATA INGESTION & CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bank-building.png", width=56)
    st.title("FinPulse AI")
    st.caption("**Micro-Enterprise Financial Health & Credit Readiness Engine**\n*IBM Bharat Cares Internship*")
    st.divider()

    st.subheader("1. Load Micro-Business Persona")
    persona_choice = st.selectbox(
        "Choose Built-in Persona Dataset:",
        options=[
            ("persona_a", "Persona A: Kirana Store (Prime / Steady)"),
            ("persona_b", "Persona B: Seasonal Artisan (High Risk / Volatile)"),
            ("persona_c", "Persona C: Street Food Vendor (Thin Margin / Growing)")
        ],
        format_func=lambda x: x[1]
    )

    if "current_df" not in st.session_state:
        # Load default Persona A
        st.session_state["current_df"] = PersonaGenerator.generate_persona_a(days=180)
        st.session_state["dataset_source"] = "Persona A: Laxmi Kirana General Store"

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📥 Load Persona", use_container_width=True, type="primary"):
            st.session_state["current_df"] = PersonaGenerator.get_persona_dataset(persona_choice[0], days=180)
            st.session_state["dataset_source"] = PersonaGenerator.PERSONAS[persona_choice[0]]["name"]
            st.rerun()

    with col_btn2:
        if st.button("🔄 Reset to Default", use_container_width=True):
            st.session_state["current_df"] = PersonaGenerator.generate_persona_a(days=180)
            st.session_state["dataset_source"] = PersonaGenerator.PERSONAS["persona_a"]["name"]
            st.rerun()

    st.divider()

    st.subheader("2. Upload Custom Ledger")
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel Ledger",
        type=["csv", "xlsx"],
        help="Columns required: Date, Transaction_Type, Category, Amount, Payment_Mode, Description"
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_excel(uploaded_file)
            
            # Simple validation
            missing_cols = [c for c in ["Date", "Transaction_Type", "Amount"] if c.lower() not in [x.lower() for x in df_upload.columns]]
            if missing_cols:
                st.error(f"Missing mandatory columns: {missing_cols}")
            else:
                st.session_state["current_df"] = df_upload
                st.session_state["dataset_source"] = f"Custom Upload: {uploaded_file.name}"
                st.success(f"Loaded {len(df_upload)} records successfully!")
        except Exception as e:
            st.error(f"Error parsing file: {e}")

    st.divider()
    st.info("💡 **Tip**: Underwriting model computes mathematical ratios (DSCR, CV, Runway) deterministically without generative hallucination.")


# -----------------------------------------------------------------------------
# MAIN APP EXECUTION
# -----------------------------------------------------------------------------
df_active = st.session_state.get("current_df", pd.DataFrame())

if df_active.empty:
    st.warning("No transaction data loaded. Please select a persona or upload a ledger.")
    st.stop()

# Initialize Analytical Engine
analyzer = FinancialAnalyzer(df_active)
kpis = analyzer.compute_kpis()
audit = analyzer.generate_underwriting_audit(kpis)

score_info = kpis["score_breakdown"]
composite_score = score_info["composite_score"]
risk_tier = score_info["risk_tier"]
badge_class = score_info["badge_class"]

# -----------------------------------------------------------------------------
# HEADER STRIP
# -----------------------------------------------------------------------------
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.title("FinPulse AI: Credit Readiness Assessment")
    st.caption(f"📁 Active Profile: **{st.session_state.get('dataset_source', 'Active Dataset')}** | Analysis Window: **{kpis['days_span']} Days** ({kpis['transaction_count']} verified ledger entries)")

with header_col2:
    st.markdown("<div style='text-align: right; padding-top: 10px;'>", unsafe_allow_html=True)
    if badge_class == "success":
        st.markdown(f"<span class='badge-prime'>● {risk_tier}</span>", unsafe_allow_html=True)
    elif badge_class == "warning":
        st.markdown(f"<span class='badge-moderate'>▲ {risk_tier}</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span class='badge-danger'>■ {risk_tier}</span>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='margin: 0; color: #1E3A8A; font-size: 2.4rem;'>{composite_score} <span style='font-size: 1.1rem; color: #64748B;'>/ 100</span></h1>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# EXECUTIVE KPI SUMMARY CARDS
# -----------------------------------------------------------------------------
c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Gross Turnover</div>
        <div class="metric-value">₹{kpis['total_inflow']:,.0f}</div>
        <div class="metric-sub">Avg ₹{kpis['avg_daily_inflow']:,.0f}/day</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Operating Burn</div>
        <div class="metric-value">₹{kpis['total_outflow']:,.0f}</div>
        <div class="metric-sub">Avg ₹{kpis['avg_daily_burn']:,.0f}/day</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    surplus_color = "#10B981" if kpis['net_cash_flow'] >= 0 else "#EF4444"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Net Margin</div>
        <div class="metric-value" style="color: {surplus_color};">{kpis['net_margin_pct']:.1f}%</div>
        <div class="metric-sub">Surplus: ₹{kpis['net_cash_flow']:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    dscr_display = f"{kpis['dscr']:.2f}x" if kpis['dscr'] < 900 else "Debt-Free"
    dscr_color = "#10B981" if (kpis['dscr'] >= 1.5 or kpis['dscr'] >= 900) else ("#F59E0B" if kpis['dscr'] >= 1.0 else "#EF4444")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Debt Coverage (DSCR)</div>
        <div class="metric-value" style="color: {dscr_color};">{dscr_display}</div>
        <div class="metric-sub">Total Debt: ₹{kpis['total_debt_service']:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    runway_display = f"{kpis['runway_days']:.0f} Days" if kpis['runway_days'] < 900 else "Indefinite"
    runway_color = "#10B981" if kpis['runway_days'] >= 30 else ("#F59E0B" if kpis['runway_days'] >= 14 else "#EF4444")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Working Capital Runway</div>
        <div class="metric-value" style="color: {runway_color};">{runway_display}</div>
        <div class="metric-sub">Liquid cushion at daily burn</div>
    </div>
    """, unsafe_allow_html=True)

with c6:
    cv_color = "#10B981" if kpis['weekly_cv'] <= 0.6 else ("#F59E0B" if kpis['weekly_cv'] <= 1.2 else "#EF4444")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Digital Ratio / CV</div>
        <div class="metric-value" style="font-size: 1.4rem;">{kpis['digital_ratio']:.0f}% <span style="font-size: 0.9rem; color: {cv_color};">(CV: {kpis['weekly_cv']:.2f})</span></div>
        <div class="metric-sub">UPI & Bank settlements</div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# WORKSPACE TABS
# -----------------------------------------------------------------------------
tab_overview, tab_ledger, tab_audit, tab_scorecard = st.tabs([
    "📊 Executive Overview & Visuals",
    "📑 Transaction Ledger Explorer",
    "🛡️ Underwriting & Red-Flag Audit",
    "📋 Credit Readiness Scorecard & Export"
])


# -----------------------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW & VISUALS
# -----------------------------------------------------------------------------
with tab_overview:
    st.subheader("Financial Trajectory & Liquidity Dynamics")

    row1_left, row1_right = st.columns([3, 2])
    with row1_left:
        fig_monthly = FinancialVisualizer.plot_monthly_timeline(analyzer.df)
        st.plotly_chart(fig_monthly, use_container_width=True)

    with row1_right:
        fig_radar = FinancialVisualizer.plot_radar_credit_pillars(score_info)
        st.plotly_chart(fig_radar, use_container_width=True)

    row2_left, row2_right = st.columns([3, 2])
    with row2_left:
        fig_waterfall = FinancialVisualizer.plot_waterfall(kpis, analyzer.df)
        st.plotly_chart(fig_waterfall, use_container_width=True)

    with row2_right:
        fig_donut = FinancialVisualizer.plot_expense_breakdown(analyzer.df)
        st.plotly_chart(fig_donut, use_container_width=True)

    row3_left, row3_right = st.columns([3, 2])
    with row3_left:
        fig_weekly_vol = FinancialVisualizer.plot_weekly_volatility_timeline(kpis["weekly_summary"])
        st.plotly_chart(fig_weekly_vol, use_container_width=True)

    with row3_right:
        fig_modes = FinancialVisualizer.plot_payment_modes(analyzer.df)
        st.plotly_chart(fig_modes, use_container_width=True)


# -----------------------------------------------------------------------------
# TAB 2: LEDGER EXPLORER
# -----------------------------------------------------------------------------
with tab_ledger:
    st.subheader("Raw Ledger Filter & Verification")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        tx_type_filter = st.multiselect(
            "Transaction Type:",
            options=["CREDIT", "DEBIT"],
            default=["CREDIT", "DEBIT"]
        )
    with col_f2:
        available_cats = analyzer.df["Category"].unique().tolist()
        cat_filter = st.multiselect(
            "Category Filter:",
            options=available_cats,
            default=available_cats
        )
    with col_f3:
        available_modes = analyzer.df["Payment_Mode"].unique().tolist()
        mode_filter = st.multiselect(
            "Payment Mode Filter:",
            options=available_modes,
            default=available_modes
        )

    # Filter DataFrame
    filtered_df = analyzer.df[
        (analyzer.df["Transaction_Type"].isin(tx_type_filter)) &
        (analyzer.df["Category"].isin(cat_filter)) &
        (analyzer.df["Payment_Mode"].isin(mode_filter))
    ]

    st.caption(f"Showing **{len(filtered_df)}** of {len(analyzer.df)} transactions")
    
    st.dataframe(
        filtered_df[["Date", "Transaction_Type", "Category", "Amount", "Payment_Mode", "Description"]],
        use_container_width=True,
        height=450,
        column_config={
            "Amount": st.column_config.NumberColumn("Amount (₹)", format="₹%.2f"),
            "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD")
        }
    )

    # Download active filtered dataset
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Ledger (CSV)",
        data=csv_bytes,
        file_name="finpulse_ledger_export.csv",
        mime="text/csv"
    )


# -----------------------------------------------------------------------------
# TAB 3: UNDERWRITING & RED-FLAG AUDIT
# -----------------------------------------------------------------------------
with tab_audit:
    st.subheader("Automated Underwriting Diagnostic & Red-Flag Audit")
    st.write("Deterministic rule checks evaluating solvency, debt service pressure, liquidity stress, and auditability.")

    col_audit_left, col_audit_right = st.columns(2)

    with col_audit_left:
        st.markdown("### 🚨 Detected Red Flags & Risk Vulnerabilities")
        if audit["red_flags"]:
            for flag in audit["red_flags"]:
                css_class = "audit-critical" if flag["severity"] == "CRITICAL" else "audit-warning"
                badge = "🔴 CRITICAL" if flag["severity"] == "CRITICAL" else "⚠️ WARNING"
                st.markdown(f"""
                <div class="audit-card {css_class}">
                    <strong>{badge} | {flag['title']}</strong><br/>
                    <span style="font-size: 0.9rem;">{flag['description']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="audit-card audit-success">
                <strong>✅ ZERO CRITICAL RED FLAGS DETECTED</strong><br/>
                <span style="font-size: 0.9rem;">No solvency triggers, excessive debt burden, or structural cash deficits identified in this ledger.</span>
            </div>
            """, unsafe_allow_html=True)

    with col_audit_right:
        st.markdown("### 🏆 Core Underwriting Strengths")
        if audit["strengths"]:
            for strength in audit["strengths"]:
                st.markdown(f"""
                <div class="audit-card audit-success">
                    <strong>✓ {strength['title']}</strong><br/>
                    <span style="font-size: 0.9rem;">{strength['description']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No standout underwriting strengths identified under standard institutional thresholds.")

    st.markdown("---")
    st.markdown("### 💡 Recommended Micro-Credit Schemes & Action Plan")
    for rec in audit["recommendations"]:
        st.markdown(f"""
        <div class="audit-card audit-info">
            <strong>🎯 Pillar: {rec['pillar']}</strong><br/>
            <span style="font-size: 0.92rem;">{rec['action']}</span>
        </div>
        """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TAB 4: CREDIT READINESS SCORECARD & EXPORT
# -----------------------------------------------------------------------------
with tab_scorecard:
    st.subheader("Official Credit Readiness Scorecard")
    st.caption("Institutional assessment report ready for submission to Bank Microfinance Desks, NBFCs, or MUDRA officers.")

    # Scorecard Pillars breakdown
    st.markdown("#### 4-Pillar Score Breakdown")
    p_cols = st.columns(4)
    pillar_icons = {
        "Cash Flow Stability": "🌊",
        "Margin Adequacy": "📈",
        "Debt Repayment Discipline": "🤝",
        "Digital Record Verifiability": "📱"
    }

    for idx, (p_name, p_data) in enumerate(score_info["pillars"].items()):
        with p_cols[idx]:
            icon = pillar_icons.get(p_name, "⭐")
            st.metric(
                label=f"{icon} {p_name}",
                value=f"{p_data['score']} / {p_data['max']} pts",
                delta=f"{p_data['pct']}% Attainment"
            )

    st.markdown("---")

    # Structured Summary Box
    st.markdown("#### Executive Underwriting Summary Table")
    summary_data = [
        {"Indicator": "Composite Credit Readiness Score", "Value": f"{composite_score} / 100", "Assessment": risk_tier},
        {"Indicator": "Gross Operating Turnover", "Value": f"₹{kpis['total_inflow']:,.2f}", "Assessment": f"₹{kpis['avg_daily_inflow']:,.0f} / day"},
        {"Indicator": "Total Operational Burn", "Value": f"₹{kpis['total_outflow']:,.2f}", "Assessment": f"₹{kpis['avg_daily_burn']:,.0f} / day"},
        {"Indicator": "Net Cash Operating Margin", "Value": f"{kpis['net_margin_pct']:.2f}%", "Assessment": "Positive Surplus" if kpis['net_margin_pct'] > 0 else "Operating Deficit"},
        {"Indicator": "Debt Service Coverage Ratio (DSCR)", "Value": f"{kpis['dscr']:.2f}x" if kpis['dscr'] < 900 else "Debt-Free", "Assessment": "Institutional Benchmark >= 1.25x"},
        {"Indicator": "Working Capital Runway", "Value": f"{kpis['runway_days']:.1f} Days", "Assessment": "Healthy Buffer" if kpis['runway_days'] >= 21 else "Low Cushion"},
        {"Indicator": "Weekly Net Flow Volatility (CV)", "Value": f"{kpis['weekly_cv']:.2f}", "Assessment": "Low Dispersion" if kpis['weekly_cv'] < 0.6 else "High Dispersion"},
        {"Indicator": "Digital Settlement Penetration", "Value": f"{kpis['digital_ratio']:.1f}%", "Assessment": "Verifiable Audit Trail" if kpis['digital_ratio'] >= 65 else "Cash Reliant"}
    ]
    st.table(pd.DataFrame(summary_data))

    # JSON Export Package
    export_package = {
        "report_id": f"FINPULSE-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.datetime.now().isoformat(),
        "enterprise_profile": st.session_state.get("dataset_source", "Micro-Enterprise"),
        "analysis_period_days": kpis["days_span"],
        "credit_readiness": {
            "score": composite_score,
            "risk_tier": risk_tier,
            "pillars": score_info["pillars"]
        },
        "financial_metrics": {
            "gross_turnover_inr": kpis["total_inflow"],
            "total_outflow_inr": kpis["total_outflow"],
            "net_cash_flow_inr": kpis["net_cash_flow"],
            "net_margin_percentage": round(kpis["net_margin_pct"], 2),
            "dscr": round(kpis["dscr"], 2) if kpis["dscr"] < 900 else "N/A - Debt Free",
            "working_capital_runway_days": round(kpis["runway_days"], 1),
            "weekly_volatility_cv": round(kpis["weekly_cv"], 2),
            "digital_penetration_ratio_pct": round(kpis["digital_ratio"], 1)
        },
        "underwriting_audit": audit
    }

    json_str = json.dumps(export_package, indent=2, default=str)

    st.markdown("#### Export Audit Package")
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.download_button(
            label="📄 Export Scorecard as JSON (Underwriting Ready)",
            data=json_str,
            file_name=f"finpulse_credit_scorecard_{datetime.date.today().isoformat()}.json",
            mime="application/json",
            use_container_width=True
        )

    with col_exp2:
        # Printable markdown summary
        md_report = f"""# FINPULSE AI - CREDIT READINESS SCORECARD
**Report Date:** {datetime.date.today().isoformat()}  
**Enterprise Profile:** {st.session_state.get('dataset_source', 'Micro-Enterprise')}  
**Composite Credit Readiness Score:** {composite_score}/100 ({risk_tier})

---

### Core Financial Ratios:
- Gross Revenue: INR {kpis['total_inflow']:,.2f}
- Net Surplus: INR {kpis['net_cash_flow']:,.2f} ({kpis['net_margin_pct']:.2f}%)
- DSCR: {kpis['dscr']:.2f}x
- Working Capital Runway: {kpis['runway_days']:.1f} days
- Digital Penetration: {kpis['digital_ratio']:.1f}%

### Pillar Breakdown:
- Cash Flow Stability: {score_info['pillars']['Cash Flow Stability']['score']}/{score_info['pillars']['Cash Flow Stability']['max']}
- Margin Adequacy: {score_info['pillars']['Margin Adequacy']['score']}/{score_info['pillars']['Margin Adequacy']['max']}
- Debt Repayment Discipline: {score_info['pillars']['Debt Repayment Discipline']['score']}/{score_info['pillars']['Debt Repayment Discipline']['max']}
- Digital Record Verifiability: {score_info['pillars']['Digital Record Verifiability']['score']}/{score_info['pillars']['Digital Record Verifiability']['max']}
"""
        st.download_button(
            label="📋 Download Text Scorecard Report",
            data=md_report,
            file_name=f"finpulse_scorecard_summary_{datetime.date.today().isoformat()}.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.json(export_package, expanded=False)
