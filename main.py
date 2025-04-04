import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import utils
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
    """Display a personalized journey summary with cute icons and engaging visualizations"""
    st.markdown("<h2 style='text-align: center; color: #3366CC; text-shadow: 1px 1px 2px #aaa;'>✨ Your Journey Summary ✨</h2>", unsafe_allow_html=True)
    
    # Get summary parts with appropriate icons
    summary_parts = generate_journey_summary(journey_data)
    
    # Create a card-like container for the summary
    with st.container():
        # Apply custom styling to make it look like a card with enhanced animations and visual effects
        st.markdown("""
        <style>
        @keyframes gradient-animation {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        
        .journey-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 18px;
            padding: 30px;
            margin: 25px 0;
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
            animation: fadeIn 0.5s ease-out;
        }
        
        .journey-card::before {
            content: "";
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #4361EE, #3F37C9, #4CC9F0, #3F37C9, #4361EE);
            background-size: 400% 400%;
            z-index: -1;
            border-radius: 20px;
            opacity: 0.65;
            animation: gradient-animation 15s ease infinite;
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
            padding: 10px 15px;
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 10px;
            box-shadow: 0 3px 5px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            animation: fadeIn 0.5s ease-out forwards;
            opacity: 0;
        }
        
        .journey-detail:nth-child(1) { animation-delay: 0.1s; }
        .journey-detail:nth-child(2) { animation-delay: 0.2s; }
        .journey-detail:nth-child(3) { animation-delay: 0.3s; }
        .journey-detail:nth-child(4) { animation-delay: 0.4s; }
        .journey-detail:nth-child(5) { animation-delay: 0.5s; }
        .journey-detail:nth-child(6) { animation-delay: 0.6s; }
        .journey-detail:nth-child(7) { animation-delay: 0.7s; }
        
        .journey-detail:hover {
            transform: translateX(8px) scale(1.02);
            background-color: rgba(255, 255, 255, 0.9);
            box-shadow: 0 5px 10px rgba(0, 0, 0, 0.08);
        }
        
        .detail-icon {
            font-size: 1.5rem;
            margin-right: 12px;
            min-width: 28px;
            text-align: center;
            animation: float 3s ease-in-out infinite;
        }
        
        .detail-label {
            font-weight: 600;
            color: #333;
            margin-right: 10px;
        }
        
        .detail-value {
            color: #4361EE;
            font-weight: 500;
            position: relative;
            padding-bottom: 2px;
        }
        
        .detail-value::after {
            content: '';
            position: absolute;
            width: 0;
            height: 2px;
            bottom: 0;
            left: 0;
            background-color: #4CC9F0;
            transition: width 0.3s ease;
        }
        
        .journey-detail:hover .detail-value::after {
            width: 100%;
        }
        
        .journey-header {
            text-align: center;
            margin-bottom: 20px;
            font-size: 1.5rem;
            font-weight: 600;
            color: #3F37C9;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            position: relative;
            padding: 10px 5px;
            animation: fadeIn 0.5s ease-out;
        }
        
        .journey-header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 25%;
            right: 25%;
            height: 3px;
            background: linear-gradient(90deg, transparent, #4CC9F0, transparent);
        }
        
        .insight-section {
            margin-top: 25px;
            padding-top: 15px;
            border-top: 1px dashed rgba(67, 97, 238, 0.3);
            animation: fadeIn 0.8s ease-out;
        }
        
        .insight-title {
            text-align: center;
            color: #4361EE;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 15px;
            position: relative;
            display: inline-block;
            left: 50%;
            transform: translateX(-50%);
        }
        
        .insight-title::before, .insight-title::after {
            content: "✨";
            margin: 0 10px;
            font-size: 0.9rem;
            animation: float 3s ease-in-out infinite;
        }
        
        .insight-bubble-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin-top: 15px;
        }
        
        .insight-bubble {
            background-color: #f1f8ff;
            border-radius: 20px;
            padding: 10px 18px;
            margin: 5px;
            box-shadow: 0 3px 5px rgba(0, 0, 0, 0.05);
            display: inline-block;
            border-left: 3px solid #4CC9F0;
            font-style: italic;
            transition: all 0.3s ease;
            animation: fadeIn 1s ease-out forwards;
            opacity: 0;
        }
        
        .insight-bubble:nth-child(1) { animation-delay: 0.8s; }
        .insight-bubble:nth-child(2) { animation-delay: 0.9s; }
        .insight-bubble:nth-child(3) { animation-delay: 1.0s; }
        .insight-bubble:nth-child(4) { animation-delay: 1.1s; }
        .insight-bubble:nth-child(5) { animation-delay: 1.2s; }
        .insight-bubble:nth-child(6) { animation-delay: 1.3s; }
        
        .insight-bubble:hover {
            transform: translateY(-5px) scale(1.03);
            box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
            background-color: #e6f4ff;
        }
        
        .journey-footer {
            text-align: center;
            margin-top: 20px;
            font-size: 0.9rem;
            color: #777;
            font-style: italic;
            animation: fadeIn 1.5s ease-out;
        }
        
        .eco-status {
            display: inline-block;
            margin-top: 5px;
            padding: 5px 15px;
            background: linear-gradient(90deg, #E0F7FA, #B2EBF2);
            border-radius: 20px;
            font-weight: 500;
            color: #006064;
            font-size: 0.9rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .fact-box {
            background: linear-gradient(135deg, rgba(67, 97, 238, 0.1), rgba(76, 201, 240, 0.1));
            border-radius: 15px;
            padding: 15px;
            margin-top: 20px;
            border-left: 3px solid #4CC9F0;
            font-style: italic;
            animation: fadeIn 1.3s ease-out;
            position: relative;
            overflow: hidden;
        }
        
        .fact-box::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                        rgba(255,255,255, 0) 0%, 
                        rgba(255,255,255, 0.5) 50%, 
                        rgba(255,255,255, 0) 100%);
            background-size: 200% 100%;
            animation: shimmer 3s infinite;
        }
        
        .tag-item {
            display: inline-block;
            margin-right: 5px;
            padding: 4px 10px;
            background-color: rgba(67, 97, 238, 0.1);
            border-radius: 15px;
            font-size: 0.9rem;
            color: #4361EE;
            transition: all 0.3s ease;
        }
        
        .tag-item:hover {
            background-color: rgba(67, 97, 238, 0.2);
            transform: translateY(-3px);
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
        
        # Display category if available
        category = journey_data.get('Category', 'Personal')
        category_icon = utils.get_category_icon(category)
        st.markdown(f"""
        <div class="journey-detail">
            <span class="detail-icon">{category_icon}</span>
            <span class="detail-label">Category:</span>
            <span class="detail-value">{category}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Display tags if available
        tags = journey_data.get('Tags', '')
        if tags and not pd.isna(tags) and tags.strip():
            tag_list = utils.parse_tags(tags)
            if tag_list:
                tags_display = " ".join([f'<span class="tag-item">#{tag}</span>' for tag in tag_list])
                st.markdown(f"""
                <div class="journey-detail">
                    <span class="detail-icon">🏷️</span>
                    <span class="detail-label">Tags:</span>
                    <span class="detail-value">{tags_display}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Display fuel info if available
        if journey_data.get('Fuel_Consumption') and journey_data['Fuel_Consumption'] > 0:
            fuel_consumption = journey_data['Fuel_Consumption']
            fuel_economy = journey_data['Distance'] / fuel_consumption
            
            # Determine eco status
            eco_status = "⭐"
            eco_text = "Needs improvement"
            if fuel_economy > 15:
                eco_status = "⭐⭐⭐⭐⭐"
                eco_text = "Excellent!"
            elif fuel_economy > 12:
                eco_status = "⭐⭐⭐⭐"
                eco_text = "Very Good"
            elif fuel_economy > 10:
                eco_status = "⭐⭐⭐"
                eco_text = "Good"
            elif fuel_economy > 8:
                eco_status = "⭐⭐"
                eco_text = "Fair"
            
            st.markdown(f"""
            <div class="journey-detail">
                <span class="detail-icon">⛽</span>
                <span class="detail-label">Fuel:</span>
                <span class="detail-value">
                    {fuel_consumption:.1f} L (Economy: {fuel_economy:.2f} km/L)
                    <br><span class="eco-status">{eco_status} {eco_text}</span>
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # Display cost information if available
            fuel_price = journey_data.get('Fuel_Price', utils.DEFAULT_FUEL_PRICE)
            cost = journey_data.get('Cost', fuel_consumption * fuel_price)
            st.markdown(f"""
            <div class="journey-detail">
                <span class="detail-icon">💰</span>
                <span class="detail-label">Cost:</span>
                <span class="detail-value">${cost:.2f} (${fuel_price:.2f}/L)</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Display CO2 emissions
            co2 = utils.calculate_co2_emissions(journey_data['Distance'], fuel_consumption)
            
            # Determine eco impact
            eco_impact = "🌿"
            if co2 > 15:
                eco_impact = "🌲"
            elif co2 > 5:
                eco_impact = "🌱"
                
            st.markdown(f"""
            <div class="journey-detail">
                <span class="detail-icon">🌍</span>
                <span class="detail-label">CO₂ Emissions:</span>
                <span class="detail-value">{co2:.1f} kg {eco_impact}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Display additional context from summary parts (skip the first one as it's already shown)
        st.markdown('<div class="insight-section">', unsafe_allow_html=True)
        st.markdown('<div class="insight-title">Journey Insights</div>', unsafe_allow_html=True)
        
        # Create a container for the insight bubbles
        st.markdown('<div class="insight-bubble-container">', unsafe_allow_html=True)
        
        # Display each insight
        for part in summary_parts[1:]:
            st.markdown(f'<div class="insight-bubble">{part}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close insight-bubble-container
        
        # Add a fun fact in a special box
        if len(summary_parts) > 5:  # Check if we have enough summary parts
            fun_fact = summary_parts[-1]  # Usually the last one is a fun fact
            st.markdown(f'<div class="fact-box">{fun_fact}</div>', unsafe_allow_html=True)
        
        # Add a footer
        st.markdown('<div class="journey-footer">Track more journeys to improve your insights and eco-driving score!</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close insight-section
        st.markdown('</div>', unsafe_allow_html=True)  # Close journey-card
        
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
                end_reading = st.number_input(
                    "🔢 Ending Odometer Reading (km)",
                    min_value=0.0,
                    step=0.1
                )
                
                # Add a small hint about distance
                if start_reading > 0 and end_reading > start_reading:
                    distance = end_reading - start_reading
                    st.markdown(f"<p style='color: #4361EE; font-size: 0.9rem;'>Distance will be: {distance:.1f} km</p>", unsafe_allow_html=True)
                
                # Journey category
                category = st.selectbox(
                    "🗂️ Journey Category",
                    options=utils.JOURNEY_CATEGORIES,
                    index=0
                )
                
            with col2:
                purpose = st.text_input("🚩 Journey Purpose")
                
                # Tags input with placeholder
                tags = st.text_input(
                    "🏷️ Tags (comma-separated)",
                    placeholder="e.g., highway, rain, rush-hour"
                )
                
                # Fuel information
                fuel_consumption = st.number_input(
                    "⛽ Fuel Consumption (liters, optional)",
                    min_value=0.0,
                    step=0.1
                )
                
                # Fuel price with default
                fuel_price = st.number_input(
                    "💰 Fuel Price ($ per liter)",
                    min_value=0.0,
                    value=utils.DEFAULT_FUEL_PRICE,
                    step=0.01
                )
                
                # Show cost estimate if fuel consumption entered
                if fuel_consumption > 0:
                    cost = fuel_consumption * fuel_price
                    st.markdown(f"<p style='color: #4361EE; font-size: 0.9rem;'>Estimated cost: ${cost:.2f}</p>", unsafe_allow_html=True)
            
            submit_button = st.form_submit_button("💾 Save Journey")
            
            if submit_button:
                validation_error = validate_input(start_reading, end_reading, journey_date)
                
                if validation_error:
                    st.error(validation_error)
                else:
                    # Calculate journey cost
                    distance = end_reading - start_reading
                    cost = 0
                    if fuel_consumption > 0:
                        cost = utils.calculate_journey_cost(fuel_consumption, fuel_price)
                    
                    # Format tags
                    tags_formatted = utils.format_tags_for_storage(utils.parse_tags(tags))
                    
                    new_journey = {
                        'Date': journey_date,
                        'Start_Reading': start_reading,
                        'End_Reading': end_reading,
                        'Distance': distance,
                        'Purpose': purpose,
                        'Category': category,
                        'Tags': tags_formatted,
                        'Fuel_Consumption': fuel_consumption if fuel_consumption > 0 else None,
                        'Fuel_Price': fuel_price,
                        'Cost': cost
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
            options=['Date', 'Distance', 'Category', 'Cost', 'Start_Reading', 'End_Reading'],
            index=0
        )
    with col2:
        sort_order = st.radio("Sort order", ["Descending", "Ascending"], horizontal=True)
    
    # Add category filter
    if 'Category' in df.columns:
        st.markdown("<p style='margin-top: 15px; margin-bottom: 5px;'>Filter by Category:</p>", unsafe_allow_html=True)
        all_categories = ['All Categories'] + list(df['Category'].unique())
        selected_category = st.selectbox(
            "Category",
            options=all_categories,
            index=0,
            label_visibility="collapsed"
        )
    
    # Add tag filter if we have tags
    if 'Tags' in df.columns and not df['Tags'].isna().all():
        # Extract all unique tags from the dataframe
        all_tags = []
        for tags_str in df['Tags'].dropna():
            if tags_str:
                all_tags.extend(utils.parse_tags(tags_str))
        
        unique_tags = sorted(list(set(all_tags)))
        
        if unique_tags:
            st.markdown("<p style='margin-top: 15px; margin-bottom: 5px;'>Filter by Tag:</p>", unsafe_allow_html=True)
            selected_tag = st.selectbox(
                "Tag",
                options=['All Tags'] + unique_tags,
                index=0,
                label_visibility="collapsed"
            )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Apply filters
    filtered_df = df.copy()
    
    # Initialize default filter variables
    selected_category = 'All Categories'
    selected_tag = 'All Tags'
    
    # Apply category filter if available
    if 'Category' in df.columns and 'selected_category' in locals():
        if selected_category != 'All Categories':
            filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    
    # Apply tag filter if available
    if 'Tags' in df.columns and 'selected_tag' in locals():
        if selected_tag != 'All Tags':
            filtered_df = filtered_df[filtered_df['Tags'].apply(
                lambda x: selected_tag in utils.parse_tags(x) if pd.notna(x) else False
            )]
    
    # Apply sorting
    df_sorted = filtered_df.sort_values(
        by=sort_col,
        ascending=(sort_order == "Ascending")
    )
    
    # Display the data with a caption
    st.markdown("<p class='section-title'>📊 All Recorded Journeys</p>", unsafe_allow_html=True)
    # Format the dataframe for display
    format_dict = {
        'Distance': '{:.1f} km',
        'Start_Reading': '{:.1f} km',
        'End_Reading': '{:.1f} km',
        'Fuel_Consumption': '{:.1f} L'
    }
    
    # Add cost formatting if column exists
    if 'Cost' in df_sorted.columns:
        format_dict['Cost'] = '${:.2f}'
    
    # Add fuel price formatting if column exists
    if 'Fuel_Price' in df_sorted.columns:
        format_dict['Fuel_Price'] = '${:.2f}/L'
    
    st.dataframe(
        df_sorted.style.format(format_dict),
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
        if 'total_cost' in stats:
            st.metric("Total Cost", f"${stats['total_cost']:.2f}")
    
    with col2:
        st.metric("Average Journey Distance", f"{stats['avg_distance']:.1f} km")
        st.metric("Longest Journey", f"{stats['max_distance']:.1f} km")
        if 'co2_emissions' in stats:
            st.metric("CO₂ Emissions", f"{stats['co2_emissions']:.1f} kg")
    
    with col3:
        st.metric("Total Fuel Consumed", f"{stats['total_fuel']:.1f} L")
        st.metric("Average Fuel Economy", f"{stats['fuel_economy']:.2f} km/L")
        eco_rating = "⭐" * min(5, max(1, int(stats['fuel_economy'] / 3)))  # 1-5 stars
        st.metric("Eco-Driving Rating", eco_rating)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add category breakdown if available
    if 'category_stats' in stats and not stats['category_stats'].empty:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<p class='stats-section-title'>🗂️ Journey Categories Analysis</p>", unsafe_allow_html=True)
        
        # Create a pie chart for categories
        fig_cat = px.pie(
            stats['category_stats'], 
            values='Distance', 
            names='Category',
            title=None,
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        
        # Customize the pie chart
        fig_cat.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family="Arial, sans-serif",
                size=14,
                color="#333333"
            ),
            margin=dict(t=30, b=30, l=30, r=30),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        
        # Display pie chart in a column layout
        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(fig_cat, use_container_width=True)
        
        # Display category statistics in text form
        with col2:
            st.markdown("<h4 style='color: #4361EE; margin-top: 20px;'>Category Details</h4>", unsafe_allow_html=True)
            for _, row in stats['category_stats'].iterrows():
                category_icon = utils.get_category_icon(row['Category'])
                st.markdown(f"""
                <div style='margin-bottom: 15px; padding: 10px; background-color: rgba(240, 248, 255, 0.6); border-radius: 8px;'>
                    <div style='font-weight: 600; color: #333;'>{category_icon} {row['Category']}</div>
                    <div>Distance: <span style='color: #4361EE; font-weight: 500;'>{row['Distance']:.1f} km</span></div>
                    <div>Cost: <span style='color: #4361EE; font-weight: 500;'>${row['Cost']:.2f}</span></div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Environmental impact section
    if 'co2_emissions' in stats and stats['co2_emissions'] > 0:
        st.markdown("<div class='chart-container' style='border-left: 4px solid #4CC9F0;'>", unsafe_allow_html=True)
        st.markdown("<p class='stats-section-title'>🌱 Environmental Impact</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Create a gauge chart for eco-score
            eco_score = min(100, max(0, (15 / max(1, stats['fuel_economy'])) * 100))
            eco_color = "#4CC9F0" if eco_score > 70 else "#FFA500" if eco_score > 40 else "#FF4560"
            
            # Use a numeric gauge display
            st.markdown(f"""
            <div style='text-align: center; padding: 20px;'>
                <div style='font-size: 1.2rem; margin-bottom: 10px; color: #333;'>Eco-Driving Score</div>
                <div style='font-size: 3rem; font-weight: bold; color: {eco_color};'>{int(eco_score)}</div>
                <div style='font-size: 1.5rem; color: #777;'>/100</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Eco-driving tips based on score
            if eco_score > 70:
                eco_tip = "Great job! Your driving is eco-friendly."
            elif eco_score > 40:
                eco_tip = "Good, but there's room for improvement. Try to drive at a steady pace."
            else:
                eco_tip = "Your fuel economy could use improvement. Consider gentle acceleration and braking."
            
            st.markdown(f"""
            <div style='background-color: #f0f8ff; padding: 10px; border-radius: 8px; margin-top: 10px; text-align: center;'>
                <span style='font-style: italic;'>{eco_tip}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # CO2 comparison
            tree_absorption = stats['co2_emissions'] / 21  # Average tree absorbs ~21kg CO2 per year
            st.markdown(f"""
            <div style='padding: 10px; background-color: rgba(240, 248, 255, 0.6); border-radius: 8px; margin-bottom: 15px;'>
                <div style='font-weight: 600; color: #333; margin-bottom: 8px;'>Total CO₂ Emissions</div>
                <div style='font-size: 2rem; font-weight: bold; color: #4361EE;'>{stats['co2_emissions']:.1f} kg</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='padding: 10px; background-color: rgba(240, 248, 255, 0.6); border-radius: 8px;'>
                <div style='font-weight: 600; color: #333; margin-bottom: 8px;'>Equivalent to</div>
                <div style='margin-bottom: 5px;'>🌳 {tree_absorption:.1f} trees working for a year</div>
                <div style='margin-bottom: 5px;'>💡 {stats['co2_emissions'] * 3.3:.1f} hours of LED bulb use</div>
                <div style='margin-bottom: 5px;'>📱 {stats['co2_emissions'] * 55:.1f} smartphone charges</div>
            </div>
            """, unsafe_allow_html=True)
        
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
