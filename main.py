import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from utils import load_data, save_data, calculate_statistics, validate_input

# Page configuration
st.set_page_config(
    page_title="Car Mileage Tracker",
    page_icon="🚗",
    layout="wide"
)

# Initialize session state
if 'show_success' not in st.session_state:
    st.session_state.show_success = False

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

def show_journey_form(df):
    st.header("Add New Journey")
    
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
                
                df = pd.concat([df, pd.DataFrame([new_journey])], ignore_index=True)
                save_data(df)
                st.success("Journey recorded successfully!")
                st.session_state.show_success = True

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
