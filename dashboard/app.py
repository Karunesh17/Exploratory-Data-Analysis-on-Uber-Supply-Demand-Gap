import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Uber Supply-Demand Gap Analysis",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished, clean styling
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .metric-sub {
        font-size: 0.82rem;
        color: #94a3b8;
    }
    .insight-box {
        background: #ffffff;
        border-left: 4px solid #2563eb;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .tag-city {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .tag-airport {
        background-color: #fef3c7;
        color: #b45309;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Data Loading with Caching
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    candidates = [
        os.path.join(base_dir, 'data', 'uber_cleaned_data.csv'),
        'data/uber_cleaned_data.csv'
    ]
    data_path = None
    for p in candidates:
        if os.path.exists(p):
            data_path = p
            break
            
    if not data_path:
        st.error("Dataset not found! Please run data/clean_data.py first.")
        st.stop()
        
    df = pd.read_csv(data_path)
    df['request_timestamp'] = pd.to_datetime(df['request_timestamp'])
    return df

df_full = load_data()

# Sidebar: Filters
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/c/cc/Uber_logo_2018.png", width=120)
st.sidebar.title("Filter Requests")

# Location Filter
locations = ['All'] + sorted(df_full['pickup_point'].unique().tolist())
selected_location = st.sidebar.selectbox("Pickup Location", locations, index=0)

# Time Slot Filter
time_slots = ['All Slots'] + [
    'Morning Rush (5 AM - 10 AM)',
    'Evening Rush (5 PM - 10 PM)',
    'Midday (10 AM - 5 PM)',
    'Early Morning (12 AM - 5 AM)',
    'Late Night (10 PM - 12 AM)'
]
selected_slot = st.sidebar.selectbox("Time Window", time_slots, index=0)

# Hour Range Slider
hour_range = st.sidebar.slider("Request Hour Range (24h)", 0, 23, (0, 23))

# Trip Status Multi-Select
all_statuses = df_full['status'].unique().tolist()
selected_statuses = st.sidebar.multiselect("Trip Status", all_statuses, default=all_statuses)

# Filter Data
filtered_df = df_full.copy()

if selected_location != 'All':
    filtered_df = filtered_df[filtered_df['pickup_point'] == selected_location]

if selected_slot != 'All Slots':
    filtered_df = filtered_df[filtered_df['time_slot'] == selected_slot]

filtered_df = filtered_df[
    (filtered_df['request_hour'] >= hour_range[0]) & 
    (filtered_df['request_hour'] <= hour_range[1])
]

if selected_statuses:
    filtered_df = filtered_df[filtered_df['status'].isin(selected_statuses)]
else:
    st.warning("Please select at least one trip status.")
    st.stop()

# Header Section
st.title("Uber Supply-Demand Gap Analysis")
st.markdown("""
I built this dashboard to analyze why ride requests go unfulfilled, when cancellations and car shortages occur, and how ride availability compares between the City and the Airport.
""")

st.markdown("---")

# KPI Metrics Calculation
total_requests = len(filtered_df)
completed_trips = (filtered_df['status'] == 'Trip Completed').sum()
unfulfilled_trips = total_requests - completed_trips
cancelled_trips = (filtered_df['status'] == 'Cancelled').sum()
no_cars_trips = (filtered_df['status'] == 'No Cars Available').sum()

completion_rate = (completed_trips / total_requests * 100) if total_requests > 0 else 0
unfulfilled_rate = (unfulfilled_trips / total_requests * 100) if total_requests > 0 else 0
cancellation_rate = (cancelled_trips / total_requests * 100) if total_requests > 0 else 0
no_cars_rate = (no_cars_trips / total_requests * 100) if total_requests > 0 else 0

# KPI Display Cards
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Requests</div>
        <div class="metric-value">{total_requests:,}</div>
        <div class="metric-sub">All ride requests</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Completed Trips</div>
        <div class="metric-value" style="color: #16a34a;">{completed_trips:,}</div>
        <div class="metric-sub">{completion_rate:.1f}% completed</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Unfulfilled Requests</div>
        <div class="metric-value" style="color: #dc2626;">{unfulfilled_trips:,}</div>
        <div class="metric-sub">{unfulfilled_rate:.1f}% unfulfilled</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Cancellation Rate</div>
        <div class="metric-value" style="color: #ea580c;">{cancellation_rate:.1f}%</div>
        <div class="metric-sub">{cancelled_trips:,} cancelled</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">No Cars Available</div>
        <div class="metric-value" style="color: #9333ea;">{no_cars_rate:.1f}%</div>
        <div class="metric-sub">{no_cars_trips:,} without a car</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Color Palette Mapping
status_colors = {
    'Trip Completed': '#10b981',       # Emerald green
    'No Cars Available': '#8b5cf6',   # Purple
    'Cancelled': '#f97316'            # Warm Amber/Orange
}

# Row 1: Charts
c1, c2 = st.columns([1, 1.3])

with c1:
    st.subheader("1. Trip Status Breakdown")
    status_summary = filtered_df['status'].value_counts().reset_index()
    status_summary.columns = ['Status', 'Count']
    
    fig_donut = px.pie(
        status_summary, 
        names='Status', 
        values='Count',
        hole=0.55,
        color='Status',
        color_discrete_map=status_colors
    )
    fig_donut.update_traces(
        textinfo='percent+label', 
        marker=dict(line=dict(color='#ffffff', width=2))
    )
    fig_donut.update_layout(
        showlegend=False, 
        margin=dict(l=20, r=20, t=30, b=20),
        height=320
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with c2:
    st.subheader("2. Requests by Hour")
    hourly_agg = filtered_df.groupby('request_hour').agg(
        Total_Demand=('request_id', 'count'),
        Completed_Supply=('is_completed', 'sum'),
        Supply_Gap=('is_unfulfilled', 'sum')
    ).reset_index()
    
    fig_gap = go.Figure()
    fig_gap.add_trace(go.Bar(
        x=hourly_agg['request_hour'], 
        y=hourly_agg['Completed_Supply'], 
        name='Completed Trips (Supply)',
        marker_color='#10b981'
    ))
    fig_gap.add_trace(go.Bar(
        x=hourly_agg['request_hour'], 
        y=hourly_agg['Supply_Gap'], 
        name='Unfulfilled Requests (Gap)',
        marker_color='#f87171'
    ))
    fig_gap.update_layout(
        barmode='stack',
        xaxis=dict(title='Hour of the Day (0-23)', tickmode='linear', tick0=0, dtick=1),
        yaxis=dict(title='Number of Requests'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=20, r=20, t=30, b=20),
        height=320
    )
    st.plotly_chart(fig_gap, use_container_width=True)

# Row 2: Hourly Rates and Pickup Location Breakdown
c3, c4 = st.columns([1.3, 1])

with c3:
    st.subheader("3. Hourly Cancellation and Car Shortage Rates")
    hourly_rates = filtered_df.groupby('request_hour').agg(
        Total=('request_id', 'count'),
        Cancelled=('is_cancelled', 'sum'),
        No_Cars=('is_no_cars', 'sum')
    ).reset_index()
    
    hourly_rates['Cancel_Rate'] = (hourly_rates['Cancelled'] / hourly_rates['Total']) * 100
    hourly_rates['No_Cars_Rate'] = (hourly_rates['No_Cars'] / hourly_rates['Total']) * 100
    
    fig_rates = go.Figure()
    fig_rates.add_trace(go.Scatter(
        x=hourly_rates['request_hour'], 
        y=hourly_rates['Cancel_Rate'],
        mode='lines+markers',
        name='Cancellation Rate (%)',
        line=dict(color='#f97316', width=3),
        marker=dict(size=6)
    ))
    fig_rates.add_trace(go.Scatter(
        x=hourly_rates['request_hour'], 
        y=hourly_rates['No_Cars_Rate'],
        mode='lines+markers',
        name='No Cars Rate (%)',
        line=dict(color='#8b5cf6', width=3),
        marker=dict(size=6)
    ))
    fig_rates.update_layout(
        xaxis=dict(title='Hour of Day (0-23)', tickmode='linear', dtick=2),
        yaxis=dict(title='Failure Rate (%)', rangemode='tozero'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=20, r=20, t=30, b=20),
        height=320
    )
    st.plotly_chart(fig_rates, use_container_width=True)

with c4:
    st.subheader("4. Trip Status by Pickup Location")
    loc_breakdown = filtered_df.groupby(['pickup_point', 'status']).size().reset_index(name='Trips')
    
    fig_loc = px.bar(
        loc_breakdown, 
        x='pickup_point', 
        y='Trips', 
        color='status',
        barmode='group',
        color_discrete_map=status_colors,
        labels={'pickup_point': 'Pickup Location', 'Trips': 'Number of Requests'}
    )
    fig_loc.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=320
    )
    st.plotly_chart(fig_loc, use_container_width=True)

# Row 3: Heatmap and Rush Hour Breakdown
c5, c6 = st.columns([1.2, 1])

with c5:
    st.subheader("5. Unfulfilled Requests by Location and Hour")
    heatmap_data = df_full[df_full['is_unfulfilled'] == 1].groupby(
        ['pickup_point', 'request_hour']
    ).size().unstack(fill_value=0)
    
    fig_heat = px.imshow(
        heatmap_data,
        labels=dict(x="Hour of Day", y="Pickup Point", color="Unfulfilled"),
        x=heatmap_data.columns,
        y=heatmap_data.index,
        color_continuous_scale="Reds",
        aspect="auto"
    )
    fig_heat.update_layout(
        xaxis=dict(tickmode='linear', dtick=1),
        margin=dict(l=20, r=20, t=30, b=20),
        height=300
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with c6:
    st.subheader("6. Morning vs. Evening Rush Requests")
    peak_df = df_full[df_full['time_slot'].isin(['Morning Rush (5 AM - 10 AM)', 'Evening Rush (5 PM - 10 PM)'])]
    peak_summary = peak_df.groupby(['time_slot', 'status']).size().reset_index(name='Requests')
    
    fig_peak = px.bar(
        peak_summary,
        x='time_slot',
        y='Requests',
        color='status',
        color_discrete_map=status_colors,
        barmode='stack',
        labels={'time_slot': 'Peak Window'}
    )
    fig_peak.update_layout(
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=20, r=20, t=30, b=20),
        height=300
    )
    st.plotly_chart(fig_peak, use_container_width=True)

# Section: Key Observations
st.markdown("---")
st.subheader("Key Findings")

tab1, tab2, tab3 = st.tabs(["Morning City Cancellations", "Evening Airport Car Shortages", "Hypotheses & Ideas to Test"])

with tab1:
    st.markdown("""
    * **Time Window**: 5:00 AM to 9:59 AM (Hours 5 to 9).
    * **What the Data Shows**:
      - **City Morning Demand**: **1,677 requests** (Numerator: 820 cancellations, Denominator: 1,677 City requests).
      - **City Morning Cancellation Rate**: **48.90%** (820 / 1,677).
      - **Peak Single Hour**: **Hour 7 (7:00 to 7:59 AM)** reached a **50.77%** cancellation rate (164 cancellations / 323 requests).
      - **Share of All Cancellations**: **64.87%** of all 1,264 cancellations across the entire dataset happened in the City during this 5-hour window (820 / 1,264).
    * **Main Issue**: **Driver Cancellations** accounted for 68.05% of all 1,205 unfulfilled City morning requests.
    """)

with tab2:
    st.markdown("""
    * **Time Window**: 5:00 PM to 9:59 PM (Hours 17 to 21).
    * **What the Data Shows**:
      - **Airport Evening Demand**: **1,800 requests** (Numerator: 1,321 shortages, Denominator: 1,800 Airport requests).
      - **Airport Evening Car-Shortage Rate**: **73.39%** (1,321 / 1,800).
      - **Peak Single Hour**: **Hour 18 (6:00 to 6:59 PM)** reached a **76.30%** vehicle shortage rate (309 shortages / 405 requests).
      - **Share of All Car Shortages**: **49.85%** of all 2,650 car shortages across the entire dataset happened at the Airport during this 5-hour window (1,321 / 2,650).
    * **Main Issue**: **No Cars Available** accounted for 92.57% of all 1,427 unfulfilled Airport evening requests.
    """)

with tab3:
    st.markdown("""
    **Hypotheses (Requires External Data to Verify):**
    * *Morning Cancellations*: The dataset does not track driver earnings or where drivers go after dropping off a rider. A common hypothesis is that drivers in the city cancel trips to the airport in the morning because they expect few passengers returning to the city, which would mean driving back empty. Checking this would require flight arrival schedules and driver location logs.
    * *Evening Car Shortages*: The dataset does not track available cars waiting near the airport. The high number of shortages suggests that more passengers are requesting rides than there are cars nearby. Checking whether this matches flight arrival peaks would require airport flight timetables and queue logs.

    **Ideas to Test (Not Proven Results):**
    1. **Airport Scheduling**: Test sharing flight arrival schedules with drivers between 4:30 PM and 9:30 PM so more cars are near the airport before passenger demand peaks.
    2. **Morning Airport Incentives**: Test giving drivers a return-trip guarantee or return subsidy for City-to-Airport trips between 5:00 AM and 9:00 AM to see if cancellations decrease.
    3. **Separate Tracking**: Track ride completion separately for the Airport and the City, so citywide averages do not hide airport car shortages.
    """)
