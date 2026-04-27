import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import random

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="COVID-19 Health Analytics",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    .main { background-color: #0a0e1a; }

    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a0e1a 100%);
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99,179,237,0.3);
    }
    .metric-label {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #94a3b8;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        background: linear-gradient(135deg, #63b3ed, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .metric-delta {
        font-size: 12px;
        color: #68d391;
    }
    .metric-delta.negative { color: #fc8181; }

    /* Section Headers */
    .section-header {
        font-size: 18px;
        font-weight: 600;
        color: #e2e8f0;
        margin: 24px 0 16px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Hero Banner */
    .hero {
        background: linear-gradient(135deg, rgba(99,179,237,0.15) 0%, rgba(167,139,250,0.1) 100%);
        border: 1px solid rgba(99,179,237,0.2);
        border-radius: 20px;
        padding: 32px 40px;
        margin-bottom: 32px;
    }
    .hero h1 {
        font-size: 36px;
        font-weight: 700;
        color: #e2e8f0;
        margin: 0 0 8px 0;
    }
    .hero p {
        color: #94a3b8;
        font-size: 15px;
        margin: 0;
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: rgba(10,14,26,0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }

    /* Plotly charts background */
    .js-plotly-plot .plotly .bg { fill: transparent !important; }

    /* Divider */
    hr { border-color: rgba(255,255,255,0.06) !important; }

    /* Insight Box */
    .insight-box {
        background: linear-gradient(135deg, rgba(104,211,145,0.08), rgba(104,211,145,0.03));
        border-left: 3px solid #68d391;
        border-radius: 0 12px 12px 0;
        padding: 16px 20px;
        margin: 8px 0;
        color: #a0aec0;
        font-size: 14px;
        line-height: 1.6;
    }
    .insight-box strong { color: #68d391; }

    .warning-box {
        background: linear-gradient(135deg, rgba(252,129,129,0.08), rgba(252,129,129,0.03));
        border-left: 3px solid #fc8181;
        border-radius: 0 12px 12px 0;
        padding: 16px 20px;
        margin: 8px 0;
        color: #a0aec0;
        font-size: 14px;
        line-height: 1.6;
    }
    .warning-box strong { color: #fc8181; }
</style>
""", unsafe_allow_html=True)


# ─── Data Generation ───────────────────────────────────────────────────────────
@st.cache_data
def generate_covid_data():
    """Generate realistic COVID-19 synthetic dataset"""
    random.seed(42)
    np.random.seed(42)

    countries = {
        "India": {"pop": 1400, "base_cases": 44000000, "base_deaths": 530000},
        "USA": {"pop": 330, "base_cases": 103000000, "base_deaths": 1120000},
        "Brazil": {"pop": 215, "base_cases": 37000000, "base_deaths": 700000},
        "France": {"pop": 68, "base_cases": 38000000, "base_deaths": 160000},
        "Germany": {"pop": 84, "base_cases": 37000000, "base_deaths": 170000},
        "UK": {"pop": 67, "base_cases": 24000000, "base_deaths": 220000},
        "Russia": {"pop": 144, "base_cases": 22000000, "base_deaths": 395000},
        "Italy": {"pop": 60, "base_cases": 25000000, "base_deaths": 188000},
        "Japan": {"pop": 125, "base_cases": 33000000, "base_deaths": 74000},
        "Australia": {"pop": 26, "base_cases": 11000000, "base_deaths": 22000},
    }

    # Time series data (Jan 2020 – Dec 2023)
    dates = pd.date_range("2020-01-01", "2023-12-31", freq="W")
    time_data = []

    for country, info in countries.items():
        cumulative_cases = 0
        cumulative_deaths = 0
        cumulative_recovered = 0

        for i, date in enumerate(dates):
            progress = i / len(dates)

            # Simulate waves
            wave1 = 0.15 * np.exp(-((progress - 0.12) ** 2) / 0.005)
            wave2 = 0.25 * np.exp(-((progress - 0.30) ** 2) / 0.008)
            wave3 = 0.40 * np.exp(-((progress - 0.55) ** 2) / 0.010)
            wave4 = 0.20 * np.exp(-((progress - 0.78) ** 2) / 0.012)
            intensity = wave1 + wave2 + wave3 + wave4

            new_cases = int(info["base_cases"] * intensity / len(dates) * np.random.uniform(0.85, 1.15))
            new_deaths = int(new_cases * np.random.uniform(0.005, 0.025) * (1 - progress * 0.5))
            new_recovered = int(new_cases * np.random.uniform(0.88, 0.96))

            cumulative_cases += max(new_cases, 0)
            cumulative_deaths += max(new_deaths, 0)
            cumulative_recovered += max(new_recovered, 0)

            time_data.append({
                "date": date,
                "country": country,
                "new_cases": max(new_cases, 0),
                "new_deaths": max(new_deaths, 0),
                "new_recovered": max(new_recovered, 0),
                "total_cases": cumulative_cases,
                "total_deaths": cumulative_deaths,
                "total_recovered": cumulative_recovered,
                "active_cases": max(cumulative_cases - cumulative_deaths - cumulative_recovered, 0),
                "population_millions": info["pop"],
                "cases_per_million": round(cumulative_cases / info["pop"], 1),
                "deaths_per_million": round(cumulative_deaths / info["pop"], 1),
                "fatality_rate": round((cumulative_deaths / cumulative_cases * 100) if cumulative_cases > 0 else 0, 2),
                "recovery_rate": round((cumulative_recovered / cumulative_cases * 100) if cumulative_cases > 0 else 0, 2),
                "vaccination_rate": min(round(progress * 80 + np.random.uniform(-5, 5), 1), 95),
            })

    df = pd.DataFrame(time_data)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b %Y")
    return df


# ─── Load Data ─────────────────────────────────────────────────────────────────
df = generate_covid_data()

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🦠 COVID-19 Analytics")
    st.markdown("---")

    st.markdown("### 🌍 Filters")
    all_countries = sorted(df["country"].unique().tolist())
    selected_countries = st.multiselect(
        "Select Countries",
        options=all_countries,
        default=["India", "USA", "Brazil", "UK"]
    )

    year_range = st.slider(
        "Select Year Range",
        min_value=2020,
        max_value=2023,
        value=(2020, 2023)
    )

    st.markdown("---")
    st.markdown("### 📊 Metric")
    metric_choice = st.radio(
        "Primary Metric",
        ["New Cases", "New Deaths", "Active Cases", "Vaccination Rate"],
        index=0
    )

    st.markdown("---")
    st.markdown("""
    <div style='color:#64748b; font-size:12px; line-height:1.6;'>
    📌 <b style='color:#94a3b8'>Data Note</b><br>
    This dashboard uses synthetic data modeled on real COVID-19 trends for learning purposes.
    </div>
    """, unsafe_allow_html=True)

# ─── Filter Data ───────────────────────────────────────────────────────────────
if not selected_countries:
    selected_countries = all_countries

filtered_df = df[
    (df["country"].isin(selected_countries)) &
    (df["year"].between(year_range[0], year_range[1]))
]

latest = df[df["date"] == df["date"].max()]
latest_filtered = latest[latest["country"].isin(selected_countries)]

# ─── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🦠 COVID-19 Health Analytics Dashboard</h1>
    <p>Interactive data exploration • Global trends • 2020–2023 • Built with Python & Streamlit</p>
</div>
""", unsafe_allow_html=True)

# ─── KPI Cards ─────────────────────────────────────────────────────────────────
total_cases = latest_filtered["total_cases"].sum()
total_deaths = latest_filtered["total_deaths"].sum()
total_recovered = latest_filtered["total_recovered"].sum()
avg_fatality = latest_filtered["fatality_rate"].mean()
avg_vaccination = latest_filtered["vaccination_rate"].mean()
avg_recovery = latest_filtered["recovery_rate"].mean()

col1, col2, col3, col4, col5 = st.columns(5)

metrics = [
    (col1, "TOTAL CASES", f"{total_cases/1e6:.1f}M", "+2.3%", False),
    (col2, "TOTAL DEATHS", f"{total_deaths/1e6:.2f}M", "+0.8%", True),
    (col3, "RECOVERED", f"{total_recovered/1e6:.1f}M", "+3.1%", False),
    (col4, "FATALITY RATE", f"{avg_fatality:.2f}%", "-0.4%", False),
    (col5, "VACCINATED", f"{avg_vaccination:.1f}%", "+1.2%", False),
]

for col, label, value, delta, is_neg in metrics:
    with col:
        delta_class = "negative" if is_neg else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-delta {delta_class}">{delta} vs prev period</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Row 1: Time Series + Pie ──────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown('<div class="section-header">📈 Cases Over Time by Country</div>', unsafe_allow_html=True)

    metric_map = {
        "New Cases": "new_cases",
        "New Deaths": "new_deaths",
        "Active Cases": "active_cases",
        "Vaccination Rate": "vaccination_rate"
    }
    y_col = metric_map[metric_choice]

    fig_line = px.line(
        filtered_df,
        x="date", y=y_col,
        color="country",
        labels={"date": "Date", y_col: metric_choice, "country": "Country"},
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_line.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(family="Space Grotesk", color="#94a3b8"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showgrid=True),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showgrid=True),
        margin=dict(l=0, r=0, t=30, b=0),
        height=350,
    )
    fig_line.update_traces(line=dict(width=2))
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    st.markdown('<div class="section-header">🗂️ Cases Distribution</div>', unsafe_allow_html=True)

    pie_data = latest_filtered[["country", "total_cases"]].sort_values("total_cases", ascending=False)
    fig_pie = px.pie(
        pie_data, values="total_cases", names="country",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.45
    )
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color="#94a3b8"),
        legend=dict(orientation="v"),
        margin=dict(l=0, r=0, t=30, b=0),
        height=350,
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

# ─── Row 2: Bar + Scatter ──────────────────────────────────────────────────────
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.markdown('<div class="section-header">📊 Cases vs Deaths by Country</div>', unsafe_allow_html=True)

    bar_data = latest_filtered[["country", "total_cases", "total_deaths"]].sort_values("total_cases", ascending=True)
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        y=bar_data["country"], x=bar_data["total_cases"],
        name="Total Cases", orientation="h",
        marker_color="#63b3ed", opacity=0.85
    ))
    fig_bar.add_trace(go.Bar(
        y=bar_data["country"], x=bar_data["total_deaths"],
        name="Total Deaths", orientation="h",
        marker_color="#fc8181", opacity=0.85
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(family="Space Grotesk", color="#94a3b8"),
        barmode="overlay",
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=0, r=0, t=30, b=0),
        height=350,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right2:
    st.markdown('<div class="section-header">💉 Vaccination vs Fatality Rate</div>', unsafe_allow_html=True)

    scatter_data = latest_filtered[["country", "vaccination_rate", "fatality_rate", "total_cases", "population_millions"]]
    fig_scatter = px.scatter(
        scatter_data,
        x="vaccination_rate", y="fatality_rate",
        size="total_cases", color="country",
        hover_name="country",
        labels={"vaccination_rate": "Vaccination Rate (%)", "fatality_rate": "Fatality Rate (%)"},
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Set2,
        size_max=60
    )
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(family="Space Grotesk", color="#94a3b8"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=0, r=0, t=30, b=0),
        height=350,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ─── Row 3: Heatmap ────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🗓️ Monthly New Cases Heatmap</div>', unsafe_allow_html=True)

heatmap_df = filtered_df.copy()
heatmap_df["month"] = heatmap_df["date"].dt.strftime("%Y-%m")
heat_pivot = heatmap_df.groupby(["country", "month"])["new_cases"].sum().reset_index()
heat_pivot = heat_pivot.pivot(index="country", columns="month", values="new_cases").fillna(0)

fig_heat = px.imshow(
    heat_pivot,
    color_continuous_scale="Blues",
    aspect="auto",
    labels={"color": "New Cases"},
    template="plotly_dark"
)
fig_heat.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Space Grotesk", color="#94a3b8"),
    margin=dict(l=0, r=0, t=20, b=0),
    height=280,
    coloraxis_colorbar=dict(title="Cases")
)
st.plotly_chart(fig_heat, use_container_width=True)

# ─── Row 4: Recovery Rate Area + Data Table ────────────────────────────────────
col_l3, col_r3 = st.columns([3, 2])

with col_l3:
    st.markdown('<div class="section-header">💊 Recovery Rate Trend</div>', unsafe_allow_html=True)
    fig_area = px.area(
        filtered_df,
        x="date", y="recovery_rate",
        color="country",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={"recovery_rate": "Recovery Rate (%)", "date": "Date"}
    )
    fig_area.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(family="Space Grotesk", color="#94a3b8"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        margin=dict(l=0, r=0, t=30, b=0),
        height=300,
    )
    st.plotly_chart(fig_area, use_container_width=True)

with col_r3:
    st.markdown('<div class="section-header">📋 Country Summary</div>', unsafe_allow_html=True)
    summary = latest_filtered[[
        "country", "total_cases", "total_deaths",
        "fatality_rate", "recovery_rate", "vaccination_rate"
    ]].copy()
    summary.columns = ["Country", "Total Cases", "Deaths", "Fatality %", "Recovery %", "Vaccinated %"]
    summary["Total Cases"] = summary["Total Cases"].apply(lambda x: f"{x/1e6:.2f}M")
    summary["Deaths"] = summary["Deaths"].apply(lambda x: f"{x/1e3:.0f}K")
    summary = summary.sort_values("Fatality %", ascending=False).reset_index(drop=True)
    st.dataframe(summary, use_container_width=True, height=300)

# ─── Insights ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-header">🔍 Key Insights</div>', unsafe_allow_html=True)

highest_vax = latest_filtered.loc[latest_filtered["vaccination_rate"].idxmax(), "country"] if not latest_filtered.empty else "N/A"
lowest_fatal = latest_filtered.loc[latest_filtered["fatality_rate"].idxmin(), "country"] if not latest_filtered.empty else "N/A"
highest_cases = latest_filtered.loc[latest_filtered["total_cases"].idxmax(), "country"] if not latest_filtered.empty else "N/A"

col_i1, col_i2, col_i3 = st.columns(3)
with col_i1:
    st.markdown(f"""
    <div class="insight-box">
        <strong>💉 Highest Vaccination:</strong> {highest_vax} leads in vaccination coverage among selected countries, 
        showing a strong correlation with reduced fatality rates over time.
    </div>
    """, unsafe_allow_html=True)

with col_i2:
    st.markdown(f"""
    <div class="insight-box">
        <strong>📉 Lowest Fatality:</strong> {lowest_fatal} shows the lowest case fatality rate, 
        likely driven by early healthcare interventions and high recovery rates.
    </div>
    """, unsafe_allow_html=True)

with col_i3:
    st.markdown(f"""
    <div class="warning-box">
        <strong>⚠️ Most Affected:</strong> {highest_cases} recorded the highest total cases. 
        Population density and testing capacity play significant roles in this metric.
    </div>
    """, unsafe_allow_html=True)

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#475569; font-size:13px; padding: 16px 0;">
    🦠 COVID-19 Health Analytics Dashboard &nbsp;|&nbsp; Built with Python & Streamlit &nbsp;|&nbsp; Data is synthetic for educational purposes
</div>
""", unsafe_allow_html=True)
