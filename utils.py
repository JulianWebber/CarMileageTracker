import pandas as pd
import os
from datetime import datetime

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
