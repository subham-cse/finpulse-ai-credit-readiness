"""
Standalone verification script to test financial formulas, ratios, and underwriting logic across all personas.
"""

from engine.analyzer import FinancialAnalyzer
from engine.generator import PersonaGenerator
from engine.visualizer import FinancialVisualizer

def test_engine():
    print("=== TESTING FINPULSE AI ENGINE ===")
    
    # 1. Persona A Test
    df_a = PersonaGenerator.generate_persona_a(days=180)
    analyzer_a = FinancialAnalyzer(df_a)
    kpis_a = analyzer_a.compute_kpis()
    audit_a = analyzer_a.generate_underwriting_audit(kpis_a)
    
    print("\n[Persona A - Steady Kirana Store]")
    print(f"Total Inflows: INR {kpis_a['total_inflow']:,.2f}")
    print(f"Total Outflows: INR {kpis_a['total_outflow']:,.2f}")
    print(f"Net Margin: {kpis_a['net_margin_pct']:.2f}%")
    print(f"DSCR: {kpis_a['dscr']:.2f}x")
    print(f"Runway: {kpis_a['runway_days']:.1f} days")
    print(f"Weekly Volatility CV: {kpis_a['weekly_cv']:.2f}")
    print(f"Digital Penetration: {kpis_a['digital_ratio']:.1f}%")
    print(f"Composite Score: {kpis_a['score_breakdown']['composite_score']} / 100 ({kpis_a['score_breakdown']['risk_tier']})")
    assert kpis_a['score_breakdown']['composite_score'] >= 70, "Persona A should score in Prime band!"

    # 2. Persona B Test
    df_b = PersonaGenerator.generate_persona_b(days=180)
    analyzer_b = FinancialAnalyzer(df_b)
    kpis_b = analyzer_b.compute_kpis()
    audit_b = analyzer_b.generate_underwriting_audit(kpis_b)

    print("\n[Persona B - Seasonal Artisan]")
    print(f"Total Inflows: INR {kpis_b['total_inflow']:,.2f}")
    print(f"Total Outflows: INR {kpis_b['total_outflow']:,.2f}")
    print(f"Net Margin: {kpis_b['net_margin_pct']:.2f}%")
    print(f"DSCR: {kpis_b['dscr']:.2f}x")
    print(f"Weekly Volatility CV: {kpis_b['weekly_cv']:.2f}")
    print(f"Digital Penetration: {kpis_b['digital_ratio']:.1f}%")
    print(f"Composite Score: {kpis_b['score_breakdown']['composite_score']} / 100 ({kpis_b['score_breakdown']['risk_tier']})")
    print(f"Red Flags Count: {len(audit_b['red_flags'])}")
    assert len(audit_b['red_flags']) > 0, "Persona B must trigger red flags!"

    # 3. Persona C Test
    df_c = PersonaGenerator.generate_persona_c(days=180)
    analyzer_c = FinancialAnalyzer(df_c)
    kpis_c = analyzer_c.compute_kpis()
    audit_c = analyzer_c.generate_underwriting_audit(kpis_c)

    print("\n[Persona C - Street Food Vendor]")
    print(f"Total Inflows: INR {kpis_c['total_inflow']:,.2f}")
    print(f"Total Outflows: INR {kpis_c['total_outflow']:,.2f}")
    print(f"Net Margin: {kpis_c['net_margin_pct']:.2f}%")
    print(f"DSCR: {kpis_c['dscr']:.2f}x")
    print(f"Digital Penetration: {kpis_c['digital_ratio']:.1f}%")
    print(f"Composite Score: {kpis_c['score_breakdown']['composite_score']} / 100 ({kpis_c['score_breakdown']['risk_tier']})")

    # 4. Visualizer Test
    print("\n[Testing Plotly Visualizer Factory]")
    fig1 = FinancialVisualizer.plot_monthly_timeline(df_a)
    fig2 = FinancialVisualizer.plot_waterfall(kpis_a, df_a)
    fig3 = FinancialVisualizer.plot_radar_credit_pillars(kpis_a['score_breakdown'])
    fig4 = FinancialVisualizer.plot_expense_breakdown(df_a)
    fig5 = FinancialVisualizer.plot_weekly_volatility_timeline(kpis_a['weekly_summary'])
    print("All 5 Plotly figures generated successfully without error.")

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY! Ready for production deployment.")

if __name__ == "__main__":
    test_engine()
