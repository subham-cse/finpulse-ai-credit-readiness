"""
FinPulse AI - Interactive Financial Visualizer Factory
Creates high-contrast, executive-ready Plotly charts for financial health indicators.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


class FinancialVisualizer:
    """
    Factory for producing Plotly visualizations:
    - Monthly Cash Inflow vs Outflow with Net Surplus balance
    - Revenue to Operating Surplus Waterfall chart
    - 4-Pillar Credit Readiness Radar / Spider chart
    - Expense Breakdown Donut chart (Operational vs Debt Servicing)
    - Weekly Net Cash Flow Volatility distribution & timeline
    """

    COLOR_PRIMARY = "#2563EB"     # Royal Blue
    COLOR_SUCCESS = "#10B981"     # Emerald Green
    COLOR_WARNING = "#F59E0B"     # Amber
    COLOR_DANGER = "#EF4444"      # Rose Red
    COLOR_PURPLE = "#8B5CF6"      # Indigo / Violet
    COLOR_BG_CARD = "#FFFFFF"

    @classmethod
    def plot_monthly_timeline(cls, df: pd.DataFrame) -> go.Figure:
        """
        Dual-axis chart: Monthly Inflow vs Outflow bars with cumulative net line.
        """
        if df.empty:
            return go.Figure()

        temp = df.copy()
        temp["Date"] = pd.to_datetime(temp["Date"])
        temp["YearMonth"] = temp["Date"].dt.to_period("M").astype(str)

        grouped = temp.groupby(["YearMonth", "Transaction_Type"])["Amount"].sum().unstack(fill_value=0.0)
        
        if "CREDIT" not in grouped.columns:
            grouped["CREDIT"] = 0.0
        if "DEBIT" not in grouped.columns:
            grouped["DEBIT"] = 0.0

        grouped["Net"] = grouped["CREDIT"] - grouped["DEBIT"]
        grouped["Cumulative"] = grouped["Net"].cumsum()
        months = grouped.index.tolist()

        fig = go.Figure()

        # Inflow Bar
        fig.add_trace(go.Bar(
            x=months,
            y=grouped["CREDIT"],
            name="Inflow (Revenue)",
            marker_color="#10B981",
            opacity=0.85,
            hovertemplate="Month: %{x}<br>Inflow: ₹%{y:,.0f}<extra></extra>"
        ))

        # Outflow Bar
        fig.add_trace(go.Bar(
            x=months,
            y=grouped["DEBIT"],
            name="Outflow (Expenses)",
            marker_color="#EF4444",
            opacity=0.85,
            hovertemplate="Month: %{x}<br>Outflow: ₹%{y:,.0f}<extra></extra>"
        ))

        # Cumulative Balance Line
        fig.add_trace(go.Scatter(
            x=months,
            y=grouped["Cumulative"],
            name="Cumulative Surplus",
            mode="lines+markers",
            line=dict(color="#3B82F6", width=3, dash="solid"),
            marker=dict(size=8, color="#1E40AF"),
            yaxis="y2",
            hovertemplate="Month: %{x}<br>Cumulative Reserve: ₹%{y:,.0f}<extra></extra>"
        ))

        fig.update_layout(
            title="<b>Monthly Cash Flow & Cumulative Reserves Trajectory</b>",
            barmode="group",
            xaxis=dict(title="Billing Period (Month)"),
            yaxis=dict(title="Monthly Cash Flow (₹)", tickprefix="₹", rangemode="tozero"),
            yaxis2=dict(
                title="Cumulative Reserve (₹)",
                tickprefix="₹",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
            margin=dict(l=40, r=40, t=60, b=40),
            template="plotly_white",
            height=420
        )
        return fig

    @classmethod
    def plot_waterfall(cls, kpis: Dict[str, Any], df: pd.DataFrame) -> go.Figure:
        """
        Waterfall chart tracing:
        Total Inflows -> Deductions by Expense Category -> Net Retained Surplus.
        """
        debits = df[df["Transaction_Type"] == "DEBIT"]
        cat_summary = debits.groupby("Category")["Amount"].sum().to_dict()

        categories = ["Gross Inflows"]
        values = [kpis["total_inflow"]]
        measures = ["absolute"]

        # Sort expense categories by size
        sorted_cats = sorted(cat_summary.items(), key=lambda x: x[1], reverse=True)
        for cat, amt in sorted_cats:
            categories.append(f"(-) {cat}")
            values.append(-amt)
            measures.append("relative")

        categories.append("Net Operating Surplus")
        values.append(kpis["net_cash_flow"])
        measures.append("total")

        fig = go.Figure(go.Waterfall(
            name="Cash Trajectory",
            orientation="v",
            measure=measures,
            x=categories,
            textposition="outside",
            text=[f"₹{abs(v):,.0f}" for v in values],
            y=values,
            connector={"line": {"color": "#94A3B8"}},
            decreasing={"marker": {"color": "#EF4444"}},
            increasing={"marker": {"color": "#10B981"}},
            totals={"marker": {"color": "#2563EB" if kpis['net_cash_flow'] >= 0 else "#DC2626"}}
        ))

        fig.update_layout(
            title="<b>Revenue-to-Surplus Waterfall Decomposition</b>",
            showlegend=False,
            yaxis=dict(title="Amount (₹)", tickprefix="₹"),
            xaxis=dict(title="Financial Breakdown Component"),
            margin=dict(l=40, r=40, t=60, b=40),
            template="plotly_white",
            height=430
        )
        return fig

    @classmethod
    def plot_radar_credit_pillars(cls, score_breakdown: Dict[str, Any]) -> go.Figure:
        """
        Radar / Spider chart representing the 4 Credit Readiness Pillars.
        """
        pillars = score_breakdown["pillars"]
        categories = list(pillars.keys())
        # Percentage scores
        values = [pillars[c]["pct"] for c in categories]

        # Close radar loop
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]

        fig = go.Figure()

        # Target / Benchmark 75%
        fig.add_trace(go.Scatterpolar(
            r=[75] * len(categories_closed),
            theta=categories_closed,
            name="Prime Benchmark (75%)",
            line=dict(color="#94A3B8", dash="dash"),
            hoverinfo="none"
        ))

        # Enterprise Actual
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            name="Enterprise Score",
            fill="toself",
            fillcolor="rgba(37, 99, 235, 0.25)",
            line=dict(color="#2563EB", width=2.5),
            marker=dict(size=7, color="#1D4ED8")
        ))

        fig.update_layout(
            title="<b>Credit Readiness 4-Pillar Diagnostic Radar</b>",
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    ticksuffix="%",
                    tickfont=dict(size=10)
                )
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
            margin=dict(l=50, r=50, t=60, b=40),
            template="plotly_white",
            height=420
        )
        return fig

    @classmethod
    def plot_expense_breakdown(cls, df: pd.DataFrame) -> go.Figure:
        """
        Donut chart breaking down all debits into operational expenses vs debt servicing.
        """
        debits = df[df["Transaction_Type"] == "DEBIT"]
        if debits.empty:
            return go.Figure()

        cat_sum = debits.groupby("Category")["Amount"].sum().reset_index()

        fig = px.pie(
            cat_sum,
            values="Amount",
            names="Category",
            hole=0.52,
            color_discrete_sequence=px.colors.qualitative.Safe,
            title="<b>Operational vs. Debt Expense Allocation</b>"
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="Category: %{label}<br>Amount: ₹%{value:,.0f} (%{percent})<extra></extra>"
        )

        fig.update_layout(
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
            margin=dict(l=30, r=40, t=60, b=30),
            template="plotly_white",
            height=380
        )
        return fig

    @classmethod
    def plot_payment_modes(cls, df: pd.DataFrame) -> go.Figure:
        """
        Stacked bar or donut chart of payment modes for digital penetration audit.
        """
        credits_df = df[df["Transaction_Type"] == "CREDIT"]
        if credits_df.empty:
            return go.Figure()

        mode_sum = credits_df.groupby("Payment_Mode")["Amount"].sum().reset_index()
        
        color_map = {
            "UPI": "#10B981",
            "Bank Transfer": "#3B82F6",
            "Cash": "#F59E0B",
            "Card": "#8B5CF6"
        }

        fig = px.pie(
            mode_sum,
            values="Amount",
            names="Payment_Mode",
            hole=0.45,
            color="Payment_Mode",
            color_discrete_map=color_map,
            title="<b>Digital vs. Cash Turnover Verifiability</b>"
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="Mode: %{label}<br>Turnover: ₹%{value:,.0f} (%{percent})<extra></extra>"
        )
        fig.update_layout(
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
            margin=dict(l=30, r=40, t=60, b=30),
            template="plotly_white",
            height=380
        )
        return fig

    @classmethod
    def plot_weekly_volatility_timeline(cls, weekly_df: pd.DataFrame) -> go.Figure:
        """
        Weekly net cash flow bar chart showing zero-line crossings and volatility swings.
        """
        if weekly_df.empty:
            return go.Figure()

        colors = ["#10B981" if val >= 0 else "#EF4444" for val in weekly_df["Net"]]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=weekly_df["Date"],
            y=weekly_df["Net"],
            marker_color=colors,
            name="Weekly Net Flow",
            hovertemplate="Week: %{x|%Y-%m-%d}<br>Net Cash Flow: ₹%{y:,.0f}<extra></extra>"
        ))

        # Add moving average line
        if len(weekly_df) >= 3:
            weekly_df["MA3"] = weekly_df["Net"].rolling(window=3, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=weekly_df["Date"],
                y=weekly_df["MA3"],
                name="3-Week Moving Avg",
                line=dict(color="#3B82F6", width=2.5)
            ))

        fig.add_hline(y=0, line_dash="dash", line_color="#475569")

        fig.update_layout(
            title="<b>Weekly Net Cash Flow Oscillations & Stability Trend</b>",
            xaxis=dict(title="Week Ending"),
            yaxis=dict(title="Net Weekly Surplus / Deficit (₹)", tickprefix="₹"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=60, b=40),
            template="plotly_white",
            height=380
        )
        return fig
