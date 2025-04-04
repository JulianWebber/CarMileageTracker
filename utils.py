import pandas as pd
import os
import re
import json
from datetime import datetime, timedelta

DATA_FILE = "data/journeys.csv"

# Journey categories
JOURNEY_CATEGORIES = [
    "Personal", "Business", "Commute", "Shopping", "Vacation", "Medical", "Education", "Family", "Other"
]

# Default fuel price (per liter)
DEFAULT_FUEL_PRICE = 1.50

def load_data():
    """Load journey data from CSV file."""
    if not os.path.exists(DATA_FILE):
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        # Create empty DataFrame with specified columns
        df = pd.DataFrame(columns=[
            'Date', 'Start_Reading', 'End_Reading', 'Distance', 'Purpose', 
            'Fuel_Consumption', 'Category', 'Tags', 'Fuel_Price', 'Cost'
        ])
        df.to_csv(DATA_FILE, index=False)
        return df
    
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    
    # Handle backward compatibility for new columns
    if 'Category' not in df.columns:
        df['Category'] = 'Personal'  # Default category
    
    if 'Tags' not in df.columns:
        df['Tags'] = ''  # Empty tags by default
    
    if 'Fuel_Price' not in df.columns:
        df['Fuel_Price'] = DEFAULT_FUEL_PRICE
    
    if 'Cost' not in df.columns:
        # Calculate cost for existing entries
        df['Cost'] = df.apply(
            lambda row: calculate_journey_cost(row['Fuel_Consumption'], row['Fuel_Price']), 
            axis=1
        )
    
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
    category = journey_data.get('Category', 'Personal')
    tags = journey_data.get('Tags', '')
    fuel_price = journey_data.get('Fuel_Price', DEFAULT_FUEL_PRICE)
    cost = journey_data.get('Cost', 0)
    
    # Calculate cost if not provided
    if cost == 0 and fuel and not pd.isna(fuel) and fuel > 0:
        cost = calculate_journey_cost(fuel, fuel_price)
    
    # Calculate CO2 emissions
    co2_emissions = calculate_co2_emissions(distance, fuel)
    
    # Base summary parts
    summary_parts = []
    
    # Get category icon
    category_icon = get_category_icon(category)
    
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
    
    # Add primary journey purpose statement with icon and category
    summary_parts.append(f"{primary_icon} You drove {distance:.1f} km for {journey_data['Purpose']} {category_icon}")
    
    # Add distance classification with icon
    if distance < 5:
        summary_parts.append("🏠 Just a quick local trip")
    elif distance < 20:
        summary_parts.append("🏙️ A nice city drive")
    elif distance < 100:
        summary_parts.append("🛣️ A solid road trip")
    else:
        summary_parts.append("🗺️ An impressive long-distance journey")
    
    # Add fuel efficiency and cost information if fuel data exists
    if fuel and not pd.isna(fuel) and fuel > 0:
        efficiency = distance / fuel  # km/L
        if efficiency > 15:
            summary_parts.append(f"🌱 Great fuel efficiency! ({efficiency:.1f} km/L)")
        elif efficiency > 10:
            summary_parts.append(f"⛽ Decent fuel economy ({efficiency:.1f} km/L)")
        else:
            summary_parts.append(f"💨 Fuel-intensive drive ({efficiency:.1f} km/L)")
        
        # Add cost information
        summary_parts.append(f"💰 This journey cost approximately ${cost:.2f}")
    
    # Add CO2 emissions information
    if co2_emissions > 0:
        if co2_emissions < 5:
            eco_message = "🌿 Low carbon footprint"
        elif co2_emissions < 15:
            eco_message = "🌱 Moderate carbon footprint"
        else:
            eco_message = "🌍 Significant carbon footprint"
            
        summary_parts.append(f"{eco_message} ({co2_emissions:.1f} kg CO₂)")
    
    # Add tags if any
    if tags and not pd.isna(tags) and tags.strip():
        tag_list = parse_tags(tags)
        if tag_list:
            tags_display = " ".join([f"#{tag}" for tag in tag_list])
            summary_parts.append(f"🏷️ Tags: {tags_display}")
    
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

def calculate_journey_cost(fuel_consumption, fuel_price):
    """Calculate journey cost based on fuel consumption and price."""
    if pd.isna(fuel_consumption) or fuel_consumption <= 0 or pd.isna(fuel_price):
        return 0.0
    
    return fuel_consumption * fuel_price

def parse_tags(tags_string):
    """Parse tags from a comma-separated string."""
    if not tags_string or pd.isna(tags_string):
        return []
    
    # Split by comma and strip whitespace
    return [tag.strip() for tag in tags_string.split(',') if tag.strip()]

def format_tags_for_storage(tags_list):
    """Format a list of tags into a comma-separated string for storage."""
    if not tags_list:
        return ''
    
    return ', '.join(tags_list)

def get_category_icon(category):
    """Get an appropriate icon for a journey category."""
    category_icons = {
        "Personal": "👤",
        "Business": "💼",
        "Commute": "🏢",
        "Shopping": "🛒",
        "Vacation": "🏖️",
        "Medical": "🏥",
        "Education": "🎓",
        "Family": "👪",
        "Other": "📌"
    }
    
    return category_icons.get(category, "📌")

def calculate_co2_emissions(distance, fuel_consumption=None, vehicle_type='medium'):
    """
    Calculate approximate CO2 emissions for a journey.
    
    CO2 emissions are calculated based on:
    - Direct calculation if fuel consumption is provided (each liter of gasoline produces ~2.31kg of CO2)
    - Estimation based on vehicle type and distance if fuel consumption is not available
    
    Parameters:
    - distance: journey distance in km
    - fuel_consumption: fuel used in liters (optional)
    - vehicle_type: 'small', 'medium', 'large', 'suv' (used if fuel_consumption not provided)
    
    Returns CO2 emissions in kg
    """
    if fuel_consumption and not pd.isna(fuel_consumption) and fuel_consumption > 0:
        # Direct calculation based on fuel consumption
        # Each liter of gasoline produces approximately 2.31kg of CO2
        return fuel_consumption * 2.31
    else:
        # Estimation based on vehicle type and distance
        # Average CO2 emissions in kg per km
        emissions_factors = {
            'small': 0.15,    # Small car: 150g/km
            'medium': 0.19,   # Medium car: 190g/km
            'large': 0.25,    # Large car: 250g/km
            'suv': 0.30       # SUV: 300g/km
        }
        
        factor = emissions_factors.get(vehicle_type.lower(), emissions_factors['medium'])
        return distance * factor

def calculate_statistics(df):
    """Calculate journey statistics."""
    stats = {
        'total_journeys': len(df),
        'total_distance': df['Distance'].sum(),
        'avg_distance': df['Distance'].mean(),
        'max_distance': df['Distance'].max(),
        'total_fuel': df['Fuel_Consumption'].sum(),
        'fuel_economy': 0,
        'total_cost': 0,
        'co2_emissions': 0
    }
    
    # Calculate fuel economy (km/L) if fuel consumption data exists
    if not df['Fuel_Consumption'].isna().all():
        total_distance_with_fuel = df[df['Fuel_Consumption'].notna()]['Distance'].sum()
        total_fuel = df['Fuel_Consumption'].sum()
        stats['fuel_economy'] = total_distance_with_fuel / total_fuel if total_fuel > 0 else 0
    
    # Calculate total cost
    if 'Cost' in df.columns:
        stats['total_cost'] = df['Cost'].sum()
    
    # Calculate CO2 emissions
    # Sum of individual journey emissions
    stats['co2_emissions'] = df.apply(
        lambda row: calculate_co2_emissions(row['Distance'], row.get('Fuel_Consumption')),
        axis=1
    ).sum()
    
    # Calculate monthly distance
    df['Month'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m')
    monthly_distance = df.groupby('Month')['Distance'].sum().reset_index()
    stats['monthly_distance'] = monthly_distance
    
    # Calculate stats by category if available
    if 'Category' in df.columns:
        category_stats = df.groupby('Category').agg({
            'Distance': 'sum',
            'Cost': 'sum'
        }).reset_index()
        stats['category_stats'] = category_stats
    
    return stats
