import pandas as pd
import os
import re
from datetime import datetime, timedelta

DATA_FILE = "data/journeys.csv"

def load_data():
    """Load journey data from CSV file."""
    if not os.path.exists(DATA_FILE):
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        # Create empty DataFrame with specified columns
        df = pd.DataFrame(columns=[
            'Date', 'Start_Reading', 'End_Reading',
            'Distance', 'Purpose', 'Fuel_Consumption'
        ])
        df.to_csv(DATA_FILE, index=False)
        return df
    
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

def save_data(df):
    """Save journey data to CSV file."""
    df.to_csv(DATA_FILE, index=False)

def validate_input(start_reading, end_reading, journey_date):
    """Validate form input data."""
    if end_reading < start_reading:
        return "Ending odometer reading must be greater than starting reading."
    
    if journey_date > datetime.now().date():
        return "Journey date cannot be in the future."
    
    return None

def generate_journey_summary(journey_data):
    """Generate a personalized journey summary with appropriate icons."""
    
    # Extract journey details
    distance = journey_data['Distance']
    purpose = journey_data['Purpose'].lower()
    fuel = journey_data.get('Fuel_Consumption')
    date = journey_data['Date']
    
    # Base summary parts
    summary_parts = []
    
    # Set primary icon based on journey purpose keywords
    primary_icon = "🚗"  # Default car icon
    
    # Match common journey purposes to appropriate icons
    if any(word in purpose for word in ["work", "office", "job", "business"]):
        primary_icon = "💼"
    elif any(word in purpose for word in ["shop", "store", "mall", "grocery", "market"]):
        primary_icon = "🛒"
    elif any(word in purpose for word in ["school", "college", "university", "class"]):
        primary_icon = "🎓"
    elif any(word in purpose for word in ["vacation", "holiday", "trip", "travel"]):
        primary_icon = "🏖️"
    elif any(word in purpose for word in ["family", "friend", "visit", "relative"]):
        primary_icon = "👪"
    elif any(word in purpose for word in ["doctor", "hospital", "medical", "health"]):
        primary_icon = "🏥"
    elif any(word in purpose for word in ["gym", "exercise", "workout", "fitness"]):
        primary_icon = "🏋️"
    elif any(word in purpose for word in ["restaurant", "dinner", "lunch", "eat", "food"]):
        primary_icon = "🍽️"
    
    # Add primary journey purpose statement with icon
    summary_parts.append(f"{primary_icon} You drove {distance:.1f} km for {journey_data['Purpose']}")
    
    # Add distance classification with icon
    if distance < 5:
        summary_parts.append("🏠 Just a quick local trip")
    elif distance < 20:
        summary_parts.append("🏙️ A nice city drive")
    elif distance < 100:
        summary_parts.append("🛣️ A solid road trip")
    else:
        summary_parts.append("🗺️ An impressive long-distance journey")
    
    # Add fuel efficiency comment if fuel data exists
    if fuel and fuel > 0:
        efficiency = distance / fuel  # km/L
        if efficiency > 15:
            summary_parts.append("🌱 Great fuel efficiency!")
        elif efficiency > 10:
            summary_parts.append("⛽ Decent fuel economy")
        else:
            summary_parts.append("💨 Fuel-intensive drive")
    
    # Add time-of-day context
    today = datetime.now().date()
    days_diff = 0
    try:
        if hasattr(date, 'days'):  # Already a timedelta
            days_diff = date.days
        else:  # It's a date
            days_diff = (today - date).days
    except:
        # Handle the case where date might not be a valid date object
        pass
    
    if days_diff == 0:
        summary_parts.append("🗓️ Completed today")
    elif days_diff == 1:
        summary_parts.append("🕰️ Completed yesterday")
    elif days_diff < 7:
        summary_parts.append("📅 Completed earlier this week")
    elif days_diff < 30:
        summary_parts.append("📆 Completed earlier this month")
    else:
        summary_parts.append("🗓️ Completed some time ago")
    
    return summary_parts

def calculate_statistics(df):
    """Calculate journey statistics."""
    stats = {
        'total_journeys': len(df),
        'total_distance': df['Distance'].sum(),
        'avg_distance': df['Distance'].mean(),
        'max_distance': df['Distance'].max(),
        'total_fuel': df['Fuel_Consumption'].sum(),
        'fuel_economy': 0
    }
    
    # Calculate fuel economy (km/L) if fuel consumption data exists
    if not df['Fuel_Consumption'].isna().all():
        total_distance_with_fuel = df[df['Fuel_Consumption'].notna()]['Distance'].sum()
        total_fuel = df['Fuel_Consumption'].sum()
        stats['fuel_economy'] = total_distance_with_fuel / total_fuel if total_fuel > 0 else 0
    
    # Calculate monthly distance
    df['Month'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m')
    monthly_distance = df.groupby('Month')['Distance'].sum().reset_index()
    stats['monthly_distance'] = monthly_distance
    
    return stats
