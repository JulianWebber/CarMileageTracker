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
    st.title("🚗 Car Mileage Tracker")
    
    # Sidebar for navigation
    page = st.sidebar.radio("Navigation", ["Add Journey", "View History", "Statistics"])
    
    # Load existing data
    df = load_data()
    
    if page == "Add Journey":
        show_journey_form(df)
    elif page == "View History":
        show_journey_history(df)
    else:
        show_statistics(df)

def display_journey_summary(journey_data):
    """Display a personalized journey summary with cute icons"""
    st.subheader("✨ Your Journey Summary ✨")
    
    # Get summary parts with appropriate icons
    summary_parts = generate_journey_summary(journey_data)
    
    # Create a card-like container for the summary
    with st.container():
        # Apply custom styling to make it look like a card
        st.markdown("""
        <style>
        .journey-card {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            border-left: 5px solid #4CAF50;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display a visually appealing card with journey summary
        st.markdown('<div class="journey-card">', unsafe_allow_html=True)
        
        # Main summary line (first part)
        st.markdown(f"<h3 style='margin-top:0'>{summary_parts[0]}</h3>", unsafe_allow_html=True)
        
        # Journey details
        st.markdown(f"""
        <p><b>📏 Distance:</b> {journey_data['Distance']:.1f} km</p>
        <p><b>📌 From:</b> {journey_data['Start_Reading']:.1f} km to {journey_data['End_Reading']:.1f} km</p>
        <p><b>📅 Date:</b> {journey_data['Date']}</p>
        """, unsafe_allow_html=True)
        
        # Display fuel info if available
        if journey_data.get('Fuel_Consumption') and journey_data['Fuel_Consumption'] > 0:
            fuel_economy = journey_data['Distance'] / journey_data['Fuel_Consumption']
            st.markdown(f"""
            <p><b>⛽ Fuel:</b> {journey_data['Fuel_Consumption']:.1f} L 
            (Economy: {fuel_economy:.2f} km/L)</p>
            """, unsafe_allow_html=True)
        
        # Display additional context from summary parts (skip the first one as it's already shown)
        for part in summary_parts[1:]:
            st.markdown(f"<p>{part}</p>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Add a separator
    st.markdown("---")

def show_journey_form(df):
    st.header("Add New Journey")
    
    # Check if we need to show a journey summary from the last submission
    if st.session_state.show_success and st.session_state.last_journey is not None:
        display_journey_summary(st.session_state.last_journey)
        
        # Add button to clear the summary
        if st.button("Add Another Journey"):
            st.session_state.show_success = False
            st.session_state.last_journey = None
            st.experimental_rerun()
    else:
        with st.form("journey_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                journey_date = st.date_input(
                    "Journey Date",
                    max_value=datetime.now().date()
                )
                start_reading = st.number_input(
                    "Starting Odometer Reading (km)",
                    min_value=0.0,
                    step=0.1
                )
                fuel_consumption = st.number_input(
                    "Fuel Consumption (liters, optional)",
                    min_value=0.0,
                    step=0.1
                )
                
            with col2:
                purpose = st.text_input("Journey Purpose")
                end_reading = st.number_input(
                    "Ending Odometer Reading (km)",
                    min_value=0.0,
                    step=0.1
                )
            
            submit_button = st.form_submit_button("Save Journey")
            
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

def show_journey_history(df):
    st.header("Journey History")
    
    if df.empty:
        st.info("No journeys recorded yet.")
        return
    
    # Sorting options
    sort_col = st.selectbox(
        "Sort by",
        options=['Date', 'Distance', 'Start_Reading', 'End_Reading'],
        index=0
    )
    sort_order = st.radio("Sort order", ["Descending", "Ascending"], horizontal=True)
    
    # Apply sorting
    df_sorted = df.sort_values(
        by=sort_col,
        ascending=(sort_order == "Ascending")
    )
    
    # Display the data
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
    st.subheader("View Journey Summary")
    
    # Create selectbox with journey dates and purposes for easy identification
    journey_options = [f"{row['Date']} - {row['Purpose']} ({row['Distance']:.1f} km)" 
                      for _, row in df_sorted.iterrows()]
    
    if journey_options:
        selected_journey_idx = st.selectbox(
            "Select a journey to view detailed summary:",
            range(len(journey_options)),
            format_func=lambda idx: journey_options[idx]
        )
        
        if st.button("Show Journey Summary"):
            # Get the selected journey data
            selected_journey = df_sorted.iloc[selected_journey_idx].to_dict()
            # Display the journey summary
            display_journey_summary(selected_journey)

def show_statistics(df):
    st.header("Journey Statistics")
    
    if df.empty:
        st.info("No data available for statistics.")
        return
    
    stats = calculate_statistics(df)
    
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
    
    # Monthly distance chart
    st.subheader("Monthly Distance Traveled")
    fig = px.bar(
        stats['monthly_distance'],
        x='Month',
        y='Distance',
        title='Distance Traveled by Month'
    )
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
