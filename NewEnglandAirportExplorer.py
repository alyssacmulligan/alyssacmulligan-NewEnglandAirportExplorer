"""
Name: Alyssa Mulligan
CS230: Section 6
Data: New England Airports
URL: ***will resubmit soon  with link***
Description:
This program visualizes New England airport data through various interactive charts.
It allows users to filter airports based on region, elevation, type, and scheduled service.
The program generates a map of airport locations, a radar chart comparing airport counts and elevation,
a bar chart for average elevation, and a box plot of elevation distribution.
Users can explore key metrics like the total number of airports, and counts of large, medium, and small airports.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# State mapping dictionary
STATES = {
    "US-CT": "Connecticut",
    "US-ME": "Maine",
    "US-MA": "Massachusetts",
    "US-NH": "New Hampshire",
    "US-RI": "Rhode Island",
    "US-VT": "Vermont",
}

def load_data():
    """Load and preprocess airport data."""
    try:
        data = pd.read_csv("new_england_airports.csv").set_index("id")  # Updated to read CSV
    except FileNotFoundError:
        st.error("File not found. Please make sure 'new_england_airports.csv' is in the correct directory.")
        return pd.DataFrame()  # Return empty DataFrame if error
    data = data[data["iso_region"].isin(STATES.keys())]  # Filter by region
    data = data[data["type"].isin(["small_airport", "medium_airport", "large_airport"])]  # Filter by airport type
    data["iso_region"] = data["iso_region"].map(STATES)  # Map region codes to full names
    data = data.sort_values(by="elevation_ft")  # Sort by elevation
    data["elevation_ft"] = data["elevation_ft"].apply(lambda x: x if x > 0 else None)  # Clean elevation data
    return data


def filter_data(data, regions, elevation, airport_types, service_filter):
    """Apply user filters to the dataset."""
    filtered_data = data[
        (data["iso_region"].isin(regions)) &
        (data["elevation_ft"] <= elevation) &
        (data["type"].isin(airport_types)) &
        (data["scheduled_service"].isin(service_filter))
    ]
    return filtered_data, len(filtered_data)  # Return data and count of rows

def create_map(data):
    """Create a scatter map of airports."""
    fig = px.scatter_geo(
        data,
        lat="latitude_deg",
        lon="longitude_deg",
        hover_name="name",
        hover_data=["municipality", "ident"],
        color="iso_region",
        title="📍 Airport Locations in New England",
        color_discrete_sequence=px.colors.qualitative.T10,
    )
    st.plotly_chart(fig, use_container_width=True)

def create_elevation_chart(data):
    """Create a bar chart for average elevation by state."""
    avg_elevation = data.groupby("iso_region")["elevation_ft"].mean().reset_index()
    fig = px.bar(
        avg_elevation,
        x="iso_region",
        y="elevation_ft",
        title="🌄 Average Elevation of Airports by State",
        labels={"elevation_ft": "Average Elevation (ft)", "iso_region": "State"},
        color="iso_region",
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig.update_traces(texttemplate='%{y:.0f}', textposition='outside')  # Add labels
    st.plotly_chart(fig, use_container_width=True)

def create_radar_chart(data):
    """Create a radar chart for airport counts and elevations."""
    counts = data.groupby("iso_region").size().reset_index(name="Count")
    avg_elevation = data.groupby("iso_region")["elevation_ft"].mean().reset_index(name="Avg Elevation")
    combined = pd.merge(counts, avg_elevation, on="iso_region")

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=combined["Count"], theta=combined["iso_region"], fill="toself", name="Count"))
    fig.add_trace(go.Scatterpolar(r=combined["Avg Elevation"], theta=combined["iso_region"], fill="toself", name="Avg Elevation"))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title="📊 Radar Chart: Airport Statistics",
        template="plotly_dark",
    )
    st.plotly_chart(fig, use_container_width=True)

def create_boxplot(data):
    """Create a box plot of airport elevations."""
    fig = px.box(
        data,
        x="iso_region",
        y="elevation_ft",
        points="all",
        title="📈 Elevation Distribution by State",
        color="iso_region",
        color_discrete_sequence=px.colors.qualitative.D3,
    )
    st.plotly_chart(fig, use_container_width=True)

def display_metrics(data):
    """Display key metrics about the filtered data."""
    total_airports = len(data)
    type_counts = data["type"].value_counts()
    st.markdown("### ✈️ Key Metrics")
    st.write(f"**Total Airports:** `{total_airports}`")
    st.write(f"**Large Airports:** `{type_counts.get('large_airport', 0)}`")
    st.write(f"**Medium Airports:** `{type_counts.get('medium_airport', 0)}`")
    st.write(f"**Small Airports:** `{type_counts.get('small_airport', 0)}`")

def main():
    st.title("🛫 **New England Airport Explorer**")
    st.sidebar.header("Customize Your Filters 🎯")
    st.sidebar.markdown("---")
    st.sidebar.write("**Choose filters to explore airport data.**")

    # Sidebar controls
    data = load_data()
    if data.empty:  # Check if data is loaded successfully
        return

    region_options = list(STATES.values())
    selected_regions = st.sidebar.multiselect("Regions", region_options, default=region_options)
    max_elevation = st.sidebar.slider("Maximum Elevation (ft)", min_value=0, max_value=3000, value=2000)  # [ST1] Slider
    airport_types = ["small_airport", "medium_airport", "large_airport"]
    selected_types = st.sidebar.multiselect("Airport Types", airport_types, default=airport_types)  # [ST2] Multi-select
    commercial_only = st.sidebar.checkbox("Only Show Commercial Airports", value=False)  # [ST3] Checkbox
    service_filter = ["yes"] if commercial_only else ["yes", "no"]

    # Filter data
    filtered_data, filtered_count = filter_data(data, selected_regions, max_elevation, selected_types, service_filter)

    # Visualizations
    st.subheader("🌐 **Visualizations**")
    st.write("Explore the data through the following visualizations:")

    st.markdown("#### Airport Map")
    create_map(filtered_data)

    st.markdown("#### Average Elevation by State")
    create_elevation_chart(filtered_data)

    st.markdown("#### Airport Distribution")
    create_radar_chart(filtered_data)

    st.markdown("#### Elevation Spread")
    create_boxplot(filtered_data)

    # Display metrics at the end
    display_metrics(filtered_data)

if __name__ == "__main__":
    main()
