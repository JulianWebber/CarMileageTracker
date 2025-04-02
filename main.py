import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from utils import load_data, save_data, calculate_statistics, validate_input, generate_journey_summary

# Page configuration
st.set_page_config(
    page_title="Car Mileage Tracker",
    page_icon="🚗",
    layout="wide"
)

# Initialize session state
if 'show_success' not in st.session_state:
    st.session_state.show_success = False
if 'last_journey' not in st.session_state:
    st.session_state.last_journey = None

def main():
    # Apply global styling
    st.markdown("""
    <style>
    .main-title {
        color: #3366CC;
        text-align: center;
        margin-bottom: 30px;
        padding-bottom: 10px;
        border-bottom: 2px solid #f0f2f6;
        font-size: 2.5rem;
        text-shadow: 1px 1px 2px #aaa;
    }
    .sidebar-title {
        font-size: 1.5rem;
        color: #4361EE;
        text-align: center;
        margin-bottom: 25px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(67, 97, 238, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main title with enhanced styling
    st.markdown("<h1 class='main-title'>🚗 Car Mileage Tracker</h1>", unsafe_allow_html=True)
    
    # Sidebar styling and navigation
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>📱 Navigation</div>", unsafe_allow_html=True)
        page = st.radio("", ["Add Journey", "View History", "Statistics"], 
                       format_func=lambda x: f"{'➕' if x=='Add Journey' else '📖' if x=='View History' else '📊'} {x}")
    
    # Load existing data
    df = load_data()
    
    # Display the selected page
    if page == "Add Journey":
        show_journey_form(df)
    elif page == "View History":
        show_journey_history(df)
    else:
        show_statistics(df)

def display_journey_summary(journey_data):
    """Display a personalized journey summary with cute icons"""
    st.markdown("<h2 style='text-align: center; color: #3366CC; text-shadow: 1px 1px 2px #aaa;'>✨ Your Journey Summary ✨</h2>", unsafe_allow_html=True)
    
    # Get summary parts with appropriate icons
    summary_parts = generate_journey_summary(journey_data)
    
    # Create a card-like container for the summary
    with st.container():
        # Apply custom styling to make it look like a card
        st.markdown("""
        <style>
        .journey-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            border-left: 8px solid #4361EE;
            position: relative;
            overflow: hidden;
        }
        .journey-card::before {
            content: "";
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #4361EE, #3F37C9, #4CC9F0);
            z-index: -1;
            border-radius: 17px;
            opacity: 0.6;
        }
        .journey-card h3 {
            color: #3F37C9;
            margin-bottom: 20px;
            font-size: 1.5rem;
            font-weight: bold;
            text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.1);
        }
        .journey-detail {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            padding: 8px 12px;
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease-in-out;
        }
        .journey-detail:hover {
            transform: translateX(5px);
            background-color: rgba(255, 255, 255, 0.9);
        }
        .detail-icon {
            font-size: 1.3rem;
            margin-right: 10px;
            min-width: 24px;
            text-align: center;
        }
        .detail-label {
            font-weight: 600;
            color: #333;
            margin-right: 8px;
        }
        .detail-value {
            color: #4361EE;
            font-weight: 500;
        }
        .insight-bubble {
            background-color: #f1f8ff;
            border-radius: 20px;
            padding: 8px 15px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            display: inline-block;
            border-left: 3px solid #4CC9F0;
            font-style: italic;
        }
        .journey-header {
            text-align: center;
            margin-bottom: 15px;
            font-size: 1.4rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display a visually appealing card with journey summary
        st.markdown('<div class="journey-card">', unsafe_allow_html=True)
        
        # Main summary line (first part)
        st.markdown(f"<div class='journey-header'>{summary_parts[0]}</div>", unsafe_allow_html=True)
        
        # Journey details - each in its own styled container
        st.markdown(f"""
        <div class="journey-detail">
            <span class="detail-icon">📏</span>
            <span class="detail-label">Distance:</span>
            <span class="detail-value">{journey_data['Distance']:.1f} km</span>
        </div>
        
        <div class="journey-detail">
            <span class="detail-icon">📌</span>
            <span class="detail-label">Odometer:</span>
            <span class="detail-value">{journey_data['Start_Reading']:.1f} km → {journey_data['End_Reading']:.1f} km</span>
        </div>
        
        <div class="journey-detail">
            <span class="detail-icon">📅</span>
            <span class="detail-label">Date:</span>
            <span class="detail-value">{journey_data['Date']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Display fuel info if available
        if journey_data.get('Fuel_Consumption') and journey_data['Fuel_Consumption'] > 0:
            fuel_economy = journey_data['Distance'] / journey_data['Fuel_Consumption']
            st.markdown(f"""
            <div class="journey-detail">
                <span class="detail-icon">⛽</span>
                <span class="detail-label">Fuel:</span>
                <span class="detail-value">{journey_data['Fuel_Consumption']:.1f} L (Economy: {fuel_economy:.2f} km/L)</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Display additional context from summary parts (skip the first one as it's already shown)
        st.markdown("<div style='margin-top: 20px; text-align: center;'><h4 style='color: #4361EE; font-size: 1.1rem;'>Journey Insights</h4></div>", unsafe_allow_html=True)
        for part in summary_parts[1:]:
            st.markdown(f"<div class='insight-bubble'>{part}</div>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Add a separator
    st.markdown("<hr style='margin: 30px 0; border: 0; height: 1px; background: linear-gradient(to right, transparent, #4361EE, transparent);'>", unsafe_allow_html=True)

def show_journey_form(df):
    # Apply form styling
    st.markdown("""
    <style>
    .form-header {
        color: #3366CC;
        text-align: center;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #f0f2f6;
    }
    .form-container {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 4px solid #4361EE;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    /* Style form submit button */
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(90deg, #4361EE 0%, #4CC9F0 100%);
        color: white;
        font-weight: 500;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        width: 100%;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    /* Style form fields */
    div[data-baseweb="input"] input,
    div[data-baseweb="select"] input,
    div[data-baseweb="datepicker"] input {
        border-radius: 8px;
        border: 1px solid #ddd;
    }
    div[data-baseweb="input"]:focus-within input,
    div[data-baseweb="select"]:focus-within input,
    div[data-baseweb="datepicker"]:focus-within input {
        border: 1px solid #4361EE;
        box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='form-header'>➕ Add New Journey</h1>", unsafe_allow_html=True)
    
    # Check if we need to show a journey summary from the last submission
    if st.session_state.show_success and st.session_state.last_journey is not None:
        display_journey_summary(st.session_state.last_journey)
        
        # Add styled button to clear the summary
        st.markdown("""
        <style>
        .stButton > button {
            background: linear-gradient(90deg, #4361EE 0%, #4CC9F0 100%);
            color: white;
            font-weight: 500;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            border: none;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➕ Add Another Journey"):
                st.session_state.show_success = False
                st.session_state.last_journey = None
                st.experimental_rerun()
    else:
        # Add a container for the form
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        
        # Add form header and description
        st.markdown("<p style='text-align: center; color: #4361EE; font-size: 1.1rem; margin-bottom: 20px;'>Enter your journey details below</p>", unsafe_allow_html=True)
        
        with st.form("journey_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                journey_date = st.date_input(
                    "📅 Journey Date",
                    max_value=datetime.now().date()
                )
                start_reading = st.number_input(
                    "🔢 Starting Odometer Reading (km)",
                    min_value=0.0,
                    step=0.1
                )
                fuel_consumption = st.number_input(
                    "⛽ Fuel Consumption (liters, optional)",
                    min_value=0.0,
                    step=0.1
                )
                
            with col2:
                purpose = st.text_input("🚩 Journey Purpose")
                end_reading = st.number_input(
                    "🔢 Ending Odometer Reading (km)",
                    min_value=0.0,
                    step=0.1
                )
                
                # Add a small hint about distance
                if start_reading > 0 and end_reading > start_reading:
                    distance = end_reading - start_reading
                    st.markdown(f"<p style='color: #4361EE; font-size: 0.9rem;'>Distance will be: {distance:.1f} km</p>", unsafe_allow_html=True)
            
            submit_button = st.form_submit_button("💾 Save Journey")
            
            if submit_button:
                validation_error = validate_input(start_reading, end_reading, journey_date)
                
                if validation_error:
                    st.error(validation_error)
                else:
                    new_journey = {
                        'Date': journey_date,
                        'Start_Reading': start_reading,
                        'End_Reading': end_reading,
                        'Distance': end_reading - start_reading,
                        'Purpose': purpose,
                        'Fuel_Consumption': fuel_consumption if fuel_consumption > 0 else None
                    }
                    
                    # Store the journey data in session state for summary display
                    st.session_state.last_journey = new_journey
                    
                    df = pd.concat([df, pd.DataFrame([new_journey])], ignore_index=True)
                    save_data(df)
                    st.success("Journey recorded successfully!")
                    st.session_state.show_success = True
                    st.experimental_rerun()  # Rerun to show the summary
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_journey_history(df):
    # Apply overall styling for the page
    st.markdown("""
    <style>
    .history-header {
        color: #3366CC;
        text-align: center;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #f0f2f6;
    }
    .filter-section {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border-left: 4px solid #4361EE;
    }
    .section-title {
        color: #4361EE;
        font-size: 1.2rem;
        margin-bottom: 10px;
        font-weight: 600;
    }
    .summary-select-container {
        background-color: #f0f8ff;
        border-radius: 10px;
        padding: 20px;
        margin-top: 30px;
        border-left: 4px solid #4CC9F0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #4361EE 0%, #4CC9F0 100%);
        color: white;
        font-weight: 500;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='history-header'>📖 Journey History</h1>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("No journeys recorded yet. Add your first journey to see it here!")
        return
    
    # Sorting and filtering section
    st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>🔍 Filter & Sort Journeys</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        sort_col = st.selectbox(
            "Sort by",
            options=['Date', 'Distance', 'Start_Reading', 'End_Reading'],
            index=0
        )
    with col2:
        sort_order = st.radio("Sort order", ["Descending", "Ascending"], horizontal=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Apply sorting
    df_sorted = df.sort_values(
        by=sort_col,
        ascending=(sort_order == "Ascending")
    )
    
    # Display the data with a caption
    st.markdown("<p class='section-title'>📊 All Recorded Journeys</p>", unsafe_allow_html=True)
    st.dataframe(
        df_sorted.style.format({
            'Distance': '{:.1f} km',
            'Start_Reading': '{:.1f} km',
            'End_Reading': '{:.1f} km',
            'Fuel_Consumption': '{:.1f} L'
        }),
        use_container_width=True
    )
    
    # Allow users to view detailed summary for a specific journey
    st.markdown("<div class='summary-select-container'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>✨ View Personalized Journey Summary</p>", unsafe_allow_html=True)
    
    # Create selectbox with journey dates and purposes for easy identification
    journey_options = [f"{row['Date']} - {row['Purpose']} ({row['Distance']:.1f} km)" 
                      for _, row in df_sorted.iterrows()]
    
    if journey_options:
        selected_journey_idx = st.selectbox(
            "Select a journey to view its detailed summary:",
            range(len(journey_options)),
            format_func=lambda idx: journey_options[idx]
        )
        
        # Center the button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Show Journey Summary"):
                # Get the selected journey data
                selected_journey = df_sorted.iloc[selected_journey_idx].to_dict()
                # Display the journey summary
                display_journey_summary(selected_journey)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_statistics(df):
    # Apply overall styling for the page
    st.markdown("""
    <style>
    .stats-header {
        color: #3366CC;
        text-align: center;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #f0f2f6;
    }
    .stats-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    }
    .stats-section-title {
        color: #4361EE;
        font-size: 1.3rem;
        margin-bottom: 15px;
        font-weight: 600;
        text-align: center;
    }
    .chart-container {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-top: 25px;
        border-left: 4px solid #4CC9F0;
    }
    /* Style for Streamlit metric elements */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #4361EE !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 500 !important;
        color: #333 !important;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 0.9rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='stats-header'>📊 Journey Statistics Dashboard</h1>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("No data available for statistics. Add your first journey to see insights here!")
        return
    
    stats = calculate_statistics(df)
    
    # Create a container for the stats cards
    st.markdown("<div class='stats-card'>", unsafe_allow_html=True)
    st.markdown("<p class='stats-section-title'>🚗 Journey Overview</p>", unsafe_allow_html=True)
    
    # Display statistics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Journeys", stats['total_journeys'])
        st.metric("Total Distance", f"{stats['total_distance']:.1f} km")
    
    with col2:
        st.metric("Average Journey Distance", f"{stats['avg_distance']:.1f} km")
        st.metric("Longest Journey", f"{stats['max_distance']:.1f} km")
    
    with col3:
        st.metric("Total Fuel Consumed", f"{stats['total_fuel']:.1f} L")
        st.metric("Average Fuel Economy", f"{stats['fuel_economy']:.2f} km/L")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Monthly distance chart in its own styled container
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("<p class='stats-section-title'>📈 Monthly Travel Analysis</p>", unsafe_allow_html=True)
    
    # Configure the plot with better styling
    fig = px.bar(
        stats['monthly_distance'],
        x='Month',
        y='Distance',
        title=None,  # We'll use our custom title above
        labels={'Month': 'Month', 'Distance': 'Distance (km)'}
    )
    
    # Customize the plot appearance
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="#333333"
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode="closest",
        xaxis=dict(
            title_font=dict(size=16),
            tickfont=dict(size=14),
            gridcolor='rgba(220,220,220,0.4)'
        ),
        yaxis=dict(
            title_font=dict(size=16),
            tickfont=dict(size=14),
            gridcolor='rgba(220,220,220,0.4)'
        )
    )
    
    # Update the bar color to match our theme
    fig.update_traces(marker_color='#4361EE', marker_line_color='#3F37C9',
                     marker_line_width=1.5, opacity=0.8)
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add a tip or insight at the bottom
    if stats['total_journeys'] > 1:
        st.markdown("""
        <div style="background-color: #f1f8ff; padding: 15px; border-radius: 10px; margin-top: 20px; 
                    border-left: 3px solid #4CC9F0; font-style: italic; text-align: center;">
            <b>✨ Insight:</b> Keep logging your journeys to see more detailed statistics and trends over time!
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
