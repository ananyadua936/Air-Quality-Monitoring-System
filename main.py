
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from api_service import search_city, fetch_air_quality
from database import initialize_database, save_readings, load_all_readings
from utils import aqi_category, health_advice, calculate_statistics


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Air Quality Monitor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# 2. DARK THEME AND CSS
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: #080D18;
    color: #F1F5FF;
}

[data-testid="stSidebar"] {
    background: #0D1524;
    border-right: 1px solid #253047;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    color: #F1F5FF;
}

p, label, .stCaption {
    color: #CBD5E1;
}

[data-testid="stMetric"] {
    background: #111B2B;
    border: 1px solid #253047;
    border-radius: 16px;
    padding: 18px;
}

[data-testid="stMetricLabel"] {
    color: #94A3B8;
}

[data-testid="stMetricValue"] {
    color: #00D6FF;
}

.hero {
    background: linear-gradient(120deg, #111B2B, #102E45);
    border: 1px solid #164E63;
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 24px;
}

.hero h1 {
    color: #F1F5FF;
}

.hero p {
    color: #94A3B8;
}

.aqi-card, .pollutant-card {
    background: #111B2B;
    border: 1px solid #253047;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 10px;
}

.aqi-card {
    border-left: 7px solid var(--aqi-color);
}

.section-label, .pollutant-name {
    color: #94A3B8;
    font-size: 14px;
}

.aqi-number {
    color: var(--aqi-color);
    font-size: 48px;
    font-weight: 800;
}

.aqi-status {
    display: inline-block;
    background: var(--aqi-bg);
    color: #111827;
    border-radius: 20px;
    padding: 5px 12px;
    font-weight: 700;
}

.pollutant-value {
    color: #00D6FF;
    font-size: 26px;
    font-weight: 800;
}

.pollutant-unit {
    color: #94A3B8;
    font-size: 12px;
}

div.stButton > button,
div.stDownloadButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
}

div.stButton > button[kind="primary"] {
    background: #00B8D9;
    color: #06111B;
    border: none;
}

[data-testid="stDataFrame"] {
    border: 1px solid #253047;
    border-radius: 12px;
}

.info-note {
    background: #111B2B;
    border: 1px solid #253047;
    border-radius: 12px;
    padding: 16px;
    color: #CBD5E1;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 3. HELPER FUNCTIONS
# --------------------------------------------------
def get_aqi_colors(category):
    colors = {
        "Good": ("#16834A", "#E3F6EA"),
        "Fair": ("#927000", "#FFF5CC"),
        "Moderate": ("#C66A08", "#FFF0DD"),
        "Poor": ("#C63838", "#FDE8E8"),
        "Very Poor": ("#8B3BB5", "#F2E5FA"),
        "Extremely Poor": ("#76233F", "#F9E2EB"),
        "Unknown": ("#52657A", "#E9EEF4")
    }
    return colors.get(category, colors["Unknown"])


def show_pollutant_card(name, value, unit="µg/m³"):
    if value is None or pd.isna(value):
        display_value = "N/A"
    else:
        display_value = f"{float(value):.2f}"

    st.markdown(
        f"""
        <div class="pollutant-card">
            <div class="pollutant-name">{name}</div>
            <div class="pollutant-value">{display_value}</div>
            <div class="pollutant-unit">{unit}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# 4. INITIALIZE DATABASE AND SESSION STATE
# --------------------------------------------------
initialize_database()

if "air_frame" not in st.session_state:
    st.session_state["air_frame"] = None

if "selected_city" not in st.session_state:
    st.session_state["selected_city"] = ""


# --------------------------------------------------
# 5. SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.markdown("## 🌍 AirWatch")
    st.caption("Air Quality Monitoring System")
    st.divider()

    st.markdown("### 📍 Location Settings")

    city_name = st.text_input(
        "Enter city name",
        value=st.session_state["selected_city"] or "Chandigarh",
        placeholder="e.g. Chandigarh"
    )

    search_button = st.button(
        "🔎 Fetch / Refresh Air Quality",
        type="primary",
        use_container_width=True
    )

    st.divider()
    st.markdown("### 📊 Dashboard")
    st.caption("AQI overview")
    st.caption("Pollutant measurements")
    st.caption("Trend analysis")
    st.caption("Historical records")
    st.caption("CSV reports")

    st.divider()
    st.caption("Data source: Open-Meteo API")


# --------------------------------------------------
# 6. HEADER
# --------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🌍 Air Quality Dashboard</h1>
    <p>Monitor air-quality estimates, explore pollution trends,
    and understand potential environmental health risks.</p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 7. FETCH DATA
# --------------------------------------------------
if search_button:
    if not city_name.strip():
        st.warning("Please enter a city name.")
    else:
        try:
            with st.spinner("Finding your city..."):
                locations = search_city(city_name.strip())

            if not locations:
                st.error("City not found. Please try another city.")
            else:
                location = locations[0]
                latitude = location["latitude"]
                longitude = location["longitude"]
                selected_city = location["name"]

                with st.spinner("Fetching air-quality data..."):
                    frame = fetch_air_quality(latitude, longitude)

                if frame.empty:
                    st.error("No air-quality data was returned.")
                else:
                    frame["city"] = selected_city
                    save_readings(frame)

                    st.session_state["air_frame"] = frame
                    st.session_state["selected_city"] = selected_city

                    st.success(f"Data loaded for {selected_city}.")

        except Exception as error:
            st.error(f"Unable to retrieve data: {error}")


# --------------------------------------------------
# 8. DISPLAY DASHBOARD
# --------------------------------------------------
frame = st.session_state["air_frame"]
selected_city = st.session_state["selected_city"]

if frame is None:
    st.info(
        "👈 Enter a city in the sidebar and click "
        "**Fetch / Refresh Air Quality** to load data."
    )

else:
    st.subheader(f"📍 {selected_city}")
    st.caption(
        "Air-quality estimates and forecast data for this location."
    )

    # AQI overview
    aq_data = frame.dropna(subset=["european_aqi"]).copy()

    if not aq_data.empty:
        aq_data["_parsed_time"] = pd.to_datetime(
            aq_data["timestamp"], errors="coerce"
        )
        aq_data = aq_data.dropna(subset=["_parsed_time"])

    if not aq_data.empty:
        # Choose the timestamp closest to the current time.
        # API timestamps are in the selected location's timezone.
        now = pd.Timestamp.now()
        time_difference = (
            aq_data["_parsed_time"] - now
        ).abs()

        latest_row = aq_data.loc[time_difference.idxmin()]
        aqi = float(latest_row["european_aqi"])
        category = aqi_category(aqi)
        aqi_color, aqi_bg = get_aqi_colors(category)

        st.markdown("### 🌿 Air Quality Overview")

        left, right = st.columns([1, 2])

        with left:
            st.markdown(
                f"""
                <div class="aqi-card"
                     style="--aqi-color:{aqi_color};
                            --aqi-bg:{aqi_bg}">
                    <div class="section-label">European AQI</div>
                    <div class="aqi-number">{aqi:.1f}</div>
                    <span class="aqi-status">{category}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with right:
            st.markdown("#### Health Guidance")
            st.write(health_advice(category))
            st.caption(
                "This uses the European AQI scale, not the US AQI scale."
            )

        # Pollutant cards
        st.markdown("### 🧪 Pollutant Levels")

        pollutant_labels = [
            ("pm2_5", "PM2.5"),
            ("pm10", "PM10"),
            ("ozone", "Ozone"),
            ("nitrogen_dioxide", "Nitrogen Dioxide"),
            ("carbon_monoxide", "Carbon Monoxide")
        ]

        pollutant_cols = st.columns(5)

        for col, (key, label) in zip(
            pollutant_cols, pollutant_labels
        ):
            with col:
                show_pollutant_card(label, latest_row.get(key))

        st.caption(
            "Confirm the API's units before comparing pollutant values; "
            "units may differ between pollutants."
        )

    else:
        st.warning(
            "European AQI values are unavailable for this location."
        )

    # --------------------------------------------------
    # 9. INTERACTIVE TREND CHART
    # --------------------------------------------------
    st.divider()
    st.subheader("📈 Pollution Trend Analysis")

    chart_options = {
        "European AQI": "european_aqi",
        "PM2.5": "pm2_5",
        "PM10": "pm10",
        "Ozone": "ozone",
        "Nitrogen Dioxide": "nitrogen_dioxide",
        "Carbon Monoxide": "carbon_monoxide"
    }

    selected_chart = st.selectbox(
        "Select a metric to visualize",
        list(chart_options.keys())
    )

    chart_column = chart_options[selected_chart]

    chart_data = frame.dropna(subset=[chart_column]).copy()
    chart_data["timestamp"] = pd.to_datetime(
        chart_data["timestamp"], errors="coerce"
    )
    chart_data = chart_data.dropna(subset=["timestamp"])
    chart_data = chart_data.sort_values("timestamp")

    # IMPORTANT: The graph code belongs inside this IF block.
    if not chart_data.empty:
        fig, ax = plt.subplots(figsize=(12, 4.5))

        fig.patch.set_facecolor("#111B2B")
        ax.set_facecolor("#111B2B")

        ax.plot(
            chart_data["timestamp"],
            chart_data[chart_column],
            color="#00D6FF",
            marker="o",
            markersize=3,
            linewidth=2.5,
            markerfacecolor="#A78BFA",
            markeredgecolor="#00D6FF"
        )

        ax.fill_between(
            chart_data["timestamp"],
            chart_data[chart_column],
            color="#00D6FF",
            alpha=0.12
        )

        ax.set_title(
            f"{selected_chart} Over Time",
            color="#F1F5FF",
            fontsize=15,
            pad=16
        )

        ax.set_xlabel("Date and Time", color="#94A3B8")
        ax.set_ylabel(selected_chart, color="#94A3B8")

        ax.tick_params(
            axis="x", colors="#94A3B8", rotation=30
        )
        ax.tick_params(axis="y", colors="#94A3B8")

        ax.grid(
            True,
            color="#29374D",
            linestyle="--",
            linewidth=0.7,
            alpha=0.8
        )

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#35445B")
        ax.spines["bottom"].set_color("#35445B")

        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    else:
        st.warning(
            "No data is available for the selected metric."
        )

    # --------------------------------------------------
    # 10. DATA TABLE AND CSV EXPORT
    # --------------------------------------------------
    st.divider()
    st.subheader("📋 Air Quality Data")

    st.dataframe(
        frame,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download City Data (CSV)",
        data=frame.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_city}_air_quality.csv",
        mime="text/csv"
    )


# --------------------------------------------------
# 11. SAVED HISTORICAL RECORDS
# --------------------------------------------------
st.divider()
st.subheader("🗂️ Historical Records")

history = load_all_readings()

if not history.empty:
    st.dataframe(
        history,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download Historical Records",
        data=history.to_csv(index=False).encode("utf-8"),
        file_name="air_quality_history.csv",
        mime="text/csv"
    )
else:
    st.info("No saved records yet. Search for a city to begin.")


# --------------------------------------------------
# 12. SUMMARY STATISTICS
# --------------------------------------------------
if frame is not None:
    st.divider()
    st.subheader("📊 Summary Statistics")

    metric_options = {
        "European AQI": "european_aqi",
        "PM2.5": "pm2_5",
        "PM10": "pm10",
        "Ozone": "ozone"
    }

    metric_label = st.selectbox(
        "Choose a metric for statistics",
        list(metric_options.keys())
    )

    metric_column = metric_options[metric_label]
    values = frame[metric_column].dropna().tolist()

    average, minimum, maximum = calculate_statistics(values)

    if average is not None:
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Average {metric_label}", f"{average:.2f}")
        c2.metric(f"Minimum {metric_label}", f"{minimum:.2f}")
        c3.metric(f"Maximum {metric_label}", f"{maximum:.2f}")
    else:
        st.info("No values are available for these statistics.")


# --------------------------------------------------
# 13. FOOTER
# --------------------------------------------------
st.divider()

st.markdown("""
<div class="info-note">
    <b>About this project:</b> This educational dashboard uses the
    Open-Meteo Air Quality API. Results are model-based estimates and
    forecasts, not measurements from a physical air-quality sensor.
    Health guidance is general information and should not replace
    official local advisories.
</div>
""", unsafe_allow_html=True)
