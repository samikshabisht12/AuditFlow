import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.cleaner import clean_nrega_data, validate_data
from scraper.nrega_scraper import get_sample_data

try:
    from database.db_connect import fetch_from_db
    raw_df = fetch_from_db("SELECT * FROM nrega_data ORDER BY scraped_at ASC")
    if raw_df.empty:
        raise ValueError("Database is empty")
    df = clean_nrega_data(raw_df)
except Exception as e:
    print(f"Database connection failed: {e}. Falling back to sample data.")
    df = clean_nrega_data(get_sample_data())

validation = validate_data(df)

COLORS = {
    "primary": "#1a237e",
    "success": "#2e7d32",
    "warning": "#f57f17",
    "danger": "#c62828",
    "light_bg": "#f5f5f5",
}

def kpi_card(title, value, color):
    return html.Div([
        html.H2(value, style={"margin": "0", "fontSize": "28px", "fontWeight": "bold", "color": "white"}),
        html.P(title, style={"margin": "5px 0 0 0", "fontSize": "13px", "color": "rgba(255,255,255,0.85)"})
    ], style={
        "background": color, "padding": "20px 25px", "borderRadius": "10px",
        "flex": "1", "minWidth": "180px", "boxShadow": "0 2px 8px rgba(0,0,0,0.15)"
    })

app = dash.Dash(__name__, title="NREGA Analytics Dashboard")

app.layout = html.Div([

    html.Div([
        html.H1("NREGA Audit Analytics Dashboard",
                style={"color": "white", "margin": "0", "fontSize": "22px"}),
        html.P("Data Automation & Backend Infrastructure — Audit Analytics Dashboard",
               style={"color": "#aab4d4", "margin": "5px 0 0 0", "fontSize": "14px"})
    ], style={"background": COLORS["primary"], "padding": "20px 30px", "borderBottom": "4px solid #fdd835"}),

    html.Div([
        html.Span("Pipeline Status: "),
        html.Span(
            f"[Success] {validation['total_records']} records loaded | ",
            style={"color": COLORS["success"], "fontWeight": "bold"}
        ),
        html.Span(
            f"[Warning] {validation['issues_found']} data issues flagged"
            if validation["issues_found"] > 0 else "[Success] All data quality checks passed",
            style={"color": COLORS["warning"] if validation["issues_found"] > 0 else COLORS["success"],
                   "fontWeight": "bold"}
        ),
    ], style={"padding": "10px 30px", "background": "#e8f5e9", "fontSize": "13px", "borderBottom": "1px solid #ddd"}),

    html.Div([
        kpi_card("Total Registered Workers", f"{df['registered_workers'].sum():,.0f}", COLORS["primary"]),
        kpi_card("Job Cards Issued", f"{df['job_cards_issued'].sum():,.0f}", "#0277bd"),
        kpi_card("Households Actually Worked", f"{df['households_worked'].sum():,.0f}", COLORS["success"]),
        kpi_card("Avg Utilization Rate", f"{df['utilization_rate'].mean():.1f}%", COLORS["warning"]),
        kpi_card("High Risk States", f"{len(df[df['risk_flag'] == 'HIGH RISK'])}", COLORS["danger"]),
    ], style={"display": "flex", "gap": "15px", "padding": "20px 30px", "flexWrap": "wrap"}),

    html.Div([
        html.Div([
            html.H4("State-wise NREGA Utilization Rate",
                    style={"color": COLORS["primary"], "marginBottom": "5px"}),
            html.P("Red line = 30% risk threshold. States below are flagged for audit.",
                   style={"color": "#666", "fontSize": "12px", "margin": "0 0 10px 0"}),
            dcc.Graph(id="utilization-chart", style={"height": "350px"})
        ], style={"flex": "1", "background": "white", "padding": "20px",
                  "borderRadius": "8px", "boxShadow": "0 1px 4px rgba(0,0,0,0.1)"}),

        html.Div([
            html.H4("Job Cards Issued vs Households Worked",
                    style={"color": COLORS["primary"], "marginBottom": "5px"}),
            html.P("Points far from diagonal = low utilization = audit concern.",
                   style={"color": "#666", "fontSize": "12px", "margin": "0 0 10px 0"}),
            dcc.Graph(id="scatter-chart", style={"height": "350px"})
        ], style={"flex": "1", "background": "white", "padding": "20px",
                  "borderRadius": "8px", "boxShadow": "0 1px 4px rgba(0,0,0,0.1)"}),

    ], style={"display": "flex", "gap": "20px", "padding": "0 30px 20px 30px"}),

    html.Div([
        html.H4("Detailed State-wise Audit Data",
                style={"color": COLORS["primary"], "marginBottom": "10px"}),
        dash_table.DataTable(
            columns=[
                {"name": "State", "id": "state"},
                {"name": "Registered Workers", "id": "registered_workers"},
                {"name": "Job Cards Issued", "id": "job_cards_issued"},
                {"name": "Households Worked", "id": "households_worked"},
                {"name": "Utilization %", "id": "utilization_rate"},
                {"name": "Avg Person Days", "id": "avg_person_days"},
                {"name": "Risk Flag", "id": "risk_flag"},
            ],
            data=df[["state", "registered_workers", "job_cards_issued",
                      "households_worked", "utilization_rate", "avg_person_days", "risk_flag"]].to_dict("records"),
            style_cell={"textAlign": "left", "padding": "8px", "fontSize": "13px"},
            style_header={"backgroundColor": COLORS["primary"], "color": "white", "fontWeight": "bold"},
            style_data_conditional=[
                {"if": {"filter_query": '{risk_flag} = "HIGH RISK"'},
                 "backgroundColor": "#ffebee", "color": COLORS["danger"], "fontWeight": "bold"},
                {"if": {"filter_query": '{risk_flag} = "MEDIUM RISK"'},
                 "backgroundColor": "#fff8e1", "color": COLORS["warning"]}
            ],
            sort_action="native",
            filter_action="native",
            page_size=15,
        )
    ], style={"background": "white", "margin": "0 30px 30px 30px",
              "padding": "20px", "borderRadius": "8px", "boxShadow": "0 1px 4px rgba(0,0,0,0.1)"}),

], style={"background": COLORS["light_bg"], "minHeight": "100vh", "fontFamily": "Arial, sans-serif"})


@app.callback(Output("utilization-chart", "figure"), Input("utilization-chart", "id"))
def draw_utilization(_):
    fig = px.bar(
        df.sort_values("utilization_rate"),
        x="utilization_rate", y="state", orientation="h",
        color="utilization_rate",
        color_continuous_scale=["#c62828", "#fdd835", "#2e7d32"],
        range_color=[0, 100],
        labels={"utilization_rate": "Utilization %", "state": "State"}
    )
    fig.add_vline(x=30, line_dash="dash", line_color="red", line_width=2,
                  annotation_text="Risk Threshold (30%)", annotation_font_color="red")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10),
                      coloraxis_showscale=False, plot_bgcolor="white")
    return fig


@app.callback(Output("scatter-chart", "figure"), Input("scatter-chart", "id"))
def draw_scatter(_):
    fig = px.scatter(
        df, x="job_cards_issued", y="households_worked",
        size="person_days_generated", color="risk_flag",
        hover_name="state",
        color_discrete_map={"HIGH RISK": "#c62828", "MEDIUM RISK": "#f57f17", "NORMAL": "#2e7d32"},
        labels={"job_cards_issued": "Job Cards Issued", "households_worked": "Households Worked"}
    )
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
    return fig


if __name__ == "__main__":
    print("\nStarting Audit Analytics Dashboard...")
    print("Open your browser and go to: http://127.0.0.1:8050\n")
    app.run(debug=True, port=8050)