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
    """Generate a personalized journey summary with cute icons and engaging text."""
    
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
    
    # Enhanced primary icon selection based on journey purpose keywords
    primary_icon = "🚗"  # Default car icon
    secondary_icon = "✨"  # Default secondary icon
    
    # Match common journey purposes to appropriate icons with more specific matches
    purpose_words = purpose.split()
    
    # Work-related journeys
    if any(word in purpose for word in ["work", "office", "job", "business", "meeting", "client", "presentation"]):
        if "meeting" in purpose or "client" in purpose:
            primary_icon = "👔"
            secondary_icon = "🤝"
        elif "presentation" in purpose:
            primary_icon = "📊"
            secondary_icon = "👩‍💼"
        else:
            primary_icon = "💼"
            secondary_icon = "🏢"
    
    # Shopping journeys
    elif any(word in purpose for word in ["shop", "store", "mall", "grocery", "market", "shopping", "buy"]):
        if "grocery" in purpose or "food" in purpose:
            primary_icon = "🛒"
            secondary_icon = "🍎"
        elif "clothes" in purpose or "fashion" in purpose:
            primary_icon = "👚"
            secondary_icon = "🛍️"
        else:
            primary_icon = "🛒"
            secondary_icon = "🛍️"
    
    # Education journeys
    elif any(word in purpose for word in ["school", "college", "university", "class", "lecture", "study", "library"]):
        if "library" in purpose:
            primary_icon = "📚"
            secondary_icon = "🤓"
        else:
            primary_icon = "🎓"
            secondary_icon = "✏️"
    
    # Vacation/travel journeys
    elif any(word in purpose for word in ["vacation", "holiday", "trip", "travel", "beach", "mountain", "hike"]):
        if "beach" in purpose:
            primary_icon = "🏖️"
            secondary_icon = "🌊"
        elif "mountain" in purpose or "hike" in purpose:
            primary_icon = "⛰️"
            secondary_icon = "🥾"
        else:
            primary_icon = "✈️"
            secondary_icon = "🧳"
    
    # Family/social journeys
    elif any(word in purpose for word in ["family", "friend", "visit", "relative", "party", "dinner", "date"]):
        if "party" in purpose:
            primary_icon = "🎉"
            secondary_icon = "🥳"
        elif "dinner" in purpose or "lunch" in purpose:
            primary_icon = "🍽️"
            secondary_icon = "👪"
        elif "date" in purpose:
            primary_icon = "💖"
            secondary_icon = "🌹"
        else:
            primary_icon = "👪"
            secondary_icon = "🏡"
    
    # Health-related journeys
    elif any(word in purpose for word in ["doctor", "hospital", "medical", "health", "dentist", "appointment"]):
        if "dentist" in purpose:
            primary_icon = "🦷"
            secondary_icon = "😬"
        else:
            primary_icon = "🏥"
            secondary_icon = "🩺"
    
    # Fitness journeys
    elif any(word in purpose for word in ["gym", "exercise", "workout", "fitness", "sport", "run", "swim"]):
        if "run" in purpose or "jog" in purpose:
            primary_icon = "🏃"
            secondary_icon = "👟"
        elif "swim" in purpose:
            primary_icon = "🏊"
            secondary_icon = "💦"
        else:
            primary_icon = "🏋️"
            secondary_icon = "💪"
    
    # Food-related journeys
    elif any(word in purpose for word in ["restaurant", "dinner", "lunch", "eat", "food", "cafe", "coffee"]):
        if "coffee" in purpose or "cafe" in purpose:
            primary_icon = "☕"
            secondary_icon = "🍰"
        else:
            primary_icon = "🍽️"
            secondary_icon = "🍕"
    
    # Entertainment journeys
    elif any(word in purpose for word in ["movie", "cinema", "theater", "concert", "show", "museum", "park"]):
        if "movie" in purpose or "cinema" in purpose:
            primary_icon = "🎬"
            secondary_icon = "🍿"
        elif "concert" in purpose or "show" in purpose:
            primary_icon = "🎵"
            secondary_icon = "🎤"
        elif "museum" in purpose:
            primary_icon = "🏛️"
            secondary_icon = "🖼️"
        elif "park" in purpose:
            primary_icon = "🌳"
            secondary_icon = "🌞"
        else:
            primary_icon = "🎭"
            secondary_icon = "🎟️"
    
    # Create a more personalized and enthusiastic main summary
    travel_verbs = ["traveled", "journeyed", "ventured", "zipped", "cruised"]
    import random
    travel_verb = random.choice(travel_verbs)
    
    # Add primary journey purpose statement with icon and category
    summary_parts.append(f"{primary_icon} You {travel_verb} {distance:.1f} km for {journey_data['Purpose']} {secondary_icon} {category_icon}")
    
    # More varied and personalized distance descriptions
    if distance < 5:
        small_trip_phrases = [
            "🏠 Just a quick hop around the neighborhood",
            "🏠 A short and sweet local journey",
            "🏠 A quick errand around the corner",
            "🏠 A brief jaunt in your local area"
        ]
        summary_parts.append(random.choice(small_trip_phrases))
    elif distance < 20:
        medium_trip_phrases = [
            "🏙️ A pleasant cruise through the city",
            "🏙️ A nice drive around town",
            "🏙️ An urban adventure through the streets",
            "🏙️ Exploring the cityscape on wheels"
        ]
        summary_parts.append(random.choice(medium_trip_phrases))
    elif distance < 100:
        long_trip_phrases = [
            "🛣️ A substantial journey on the open road",
            "🛣️ Covering some serious distance today",
            "🛣️ A significant trek across the landscape",
            "🛣️ Eating up the kilometers on this road trip"
        ]
        summary_parts.append(random.choice(long_trip_phrases))
    else:
        epic_trip_phrases = [
            "🗺️ An epic voyage across the map",
            "🗺️ A remarkable long-distance expedition",
            "🗺️ Conquering vast distances on this journey",
            "🗺️ An impressive road trip adventure"
        ]
        summary_parts.append(random.choice(epic_trip_phrases))
    
    # Enhanced fuel efficiency insights with cute icons and personalized messages
    if fuel and not pd.isna(fuel) and fuel > 0:
        efficiency = distance / fuel  # km/L
        
        if efficiency > 15:
            eco_phrases = [
                f"🌱 Amazing eco-driving! Your {efficiency:.1f} km/L efficiency is saving the planet 🌎",
                f"🌿 Superb fuel economy of {efficiency:.1f} km/L! Mother Nature thanks you 🌳",
                f"🍃 Wonderful efficiency at {efficiency:.1f} km/L! Your car is purring with happiness",
                f"🌱 Eco-warrior status achieved with {efficiency:.1f} km/L! Keep up the green driving 🌿"
            ]
            summary_parts.append(random.choice(eco_phrases))
        elif efficiency > 10:
            decent_eco_phrases = [
                f"⛽ Good going with {efficiency:.1f} km/L! Your car is performing well",
                f"🚗 Solid fuel economy at {efficiency:.1f} km/L. Nice driving!",
                f"⛽ Decent efficiency of {efficiency:.1f} km/L - you're on the right track",
                f"🌱 Respectable {efficiency:.1f} km/L! A few more tweaks and you'll be an eco-star"
            ]
            summary_parts.append(random.choice(decent_eco_phrases))
        else:
            improve_eco_phrases = [
                f"💨 Fuel economy was {efficiency:.1f} km/L - gentle acceleration could help improve this",
                f"💧 {efficiency:.1f} km/L recorded - try reducing cargo weight for better efficiency",
                f"⚡ Your {efficiency:.1f} km/L could be improved with steady cruising speeds",
                f"🌬️ Economy check: {efficiency:.1f} km/L - consider maintenance for better performance"
            ]
            summary_parts.append(random.choice(improve_eco_phrases))
        
        # More personalized cost information
        cost_phrases = [
            f"💰 This adventure cost ${cost:.2f} from your treasure chest",
            f"💸 Journey expense: a modest ${cost:.2f} from your wallet",
            f"💵 The price of this trip: ${cost:.2f} well spent",
            f"🪙 Investment in this journey: ${cost:.2f} for the memories"
        ]
        summary_parts.append(random.choice(cost_phrases))
    
    # Enhanced CO2 emissions information with more engaging icons and messages
    if co2_emissions > 0:
        if co2_emissions < 5:
            eco_messages = [
                f"🌿 Tiny carbon pawprint of just {co2_emissions:.1f} kg CO₂",
                f"🍃 Earth-friendly journey with only {co2_emissions:.1f} kg CO₂ emitted",
                f"🌱 Minimal environmental impact: {co2_emissions:.1f} kg CO₂",
                f"🦋 Light as a butterfly's wing: {co2_emissions:.1f} kg CO₂"
            ]
            summary_parts.append(random.choice(eco_messages))
        elif co2_emissions < 15:
            mid_eco_messages = [
                f"🌎 Moderate eco-impact of {co2_emissions:.1f} kg CO₂",
                f"🌱 A reasonable carbon footprint: {co2_emissions:.1f} kg CO₂",
                f"🍃 Middle-of-the-road emissions at {co2_emissions:.1f} kg CO₂",
                f"🌿 Not too heavy, not too light: {co2_emissions:.1f} kg CO₂"
            ]
            summary_parts.append(random.choice(mid_eco_messages))
        else:
            high_eco_messages = [
                f"🌍 A notable carbon footprint of {co2_emissions:.1f} kg CO₂",
                f"🌳 This journey's emissions ({co2_emissions:.1f} kg CO₂) could be offset with tree planting",
                f"🌲 Higher impact journey: {co2_emissions:.1f} kg CO₂ added to your carbon account",
                f"🌊 Something to consider: this trip produced {co2_emissions:.1f} kg CO₂"
            ]
            summary_parts.append(random.choice(high_eco_messages))
    
    # Add tags with more playful framing
    if tags and not pd.isna(tags) and tags.strip():
        tag_list = parse_tags(tags)
        if tag_list:
            tags_display = " ".join([f"#{tag}" for tag in tag_list])
            tag_phrases = [
                f"🏷️ Journey vibes: {tags_display}",
                f"✨ Tagged with: {tags_display}",
                f"📌 Bookmarked as: {tags_display}",
                f"🔖 Filed under: {tags_display}"
            ]
            summary_parts.append(random.choice(tag_phrases))
    
    # More personalized time context with cute icons
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
        today_phrases = [
            "🌟 Fresh off the road today!",
            "🌞 Today's adventure logged",
            "⏰ Hot off the press: journey completed today",
            "✨ Just in: today's travel recorded"
        ]
        summary_parts.append(random.choice(today_phrases))
    elif days_diff == 1:
        yesterday_phrases = [
            "🕰️ Yesterday's road memories",
            "🌙 A journey from yesterday",
            "📆 From your travels yesterday",
            "⏱️ Logged from yesterday's adventures"
        ]
        summary_parts.append(random.choice(yesterday_phrases))
    elif days_diff < 7:
        this_week_phrases = [
            "📅 From your travels earlier this week",
            "🗓️ A recent journey this week",
            "🚗 Captured from your week's travels",
            "🌈 From the roads traveled this week"
        ]
        summary_parts.append(random.choice(this_week_phrases))
    elif days_diff < 30:
        this_month_phrases = [
            "📆 A journey from earlier this month",
            "🗓️ Part of this month's travel story",
            "🌙 From your monthly travels",
            "🚗 One of this month's road adventures"
        ]
        summary_parts.append(random.choice(this_month_phrases))
    else:
        past_phrases = [
            "🗓️ A journey from your travel archives",
            "📜 From your historical travels",
            "⏳ A blast from your driving past",
            "🔍 Recovered from your journey memories"
        ]
        summary_parts.append(random.choice(past_phrases))
    
    # Add a random fun fact or driving tip
    fun_facts = [
        "💡 Fun fact: If this trip were walking, it would be about {:.0f} steps!".format(distance * 1300),
        "🌈 Did you know? The average car spends 95% of its time parked!",
        "🔋 Eco-tip: Regular maintenance can improve fuel efficiency by up to 10%",
        "🌡️ Climate note: Properly inflated tires can save up to 3% on fuel",
        "🚦 Driving tip: Smooth acceleration can improve fuel economy significantly",
        "💧 Fun fact: It takes about 39,090 gallons of water to manufacture a new car",
        "🔄 Eco-tip: Keeping your air filter clean can improve gas mileage by up to 10%",
        "⚡ Future thought: An electric car would use about {:.1f} kWh for this journey".format(distance * 0.2)
    ]
    summary_parts.append(random.choice(fun_facts))
    
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

def calculate_carbon_offset_options(co2_emissions):
    """
    Calculate carbon offset options based on CO2 emissions.
    
    Parameters:
    - co2_emissions: CO2 emissions in kg
    
    Returns a dictionary with offset options:
    - trees: Number of trees to plant (1 tree absorbs ~21kg CO2 per year)
    - renewable_energy: kWh of renewable energy to fund
    - offset_cost: Approximate cost in USD to offset this carbon footprint
    - suggestions: List of specific carbon offset suggestions with descriptions and costs
    """
    if co2_emissions <= 0:
        return {
            'trees': 0,
            'renewable_energy': 0,
            'offset_cost': 0,
            'suggestions': []
        }
    
    # Calculate number of trees needed (rounded up)
    # Average tree absorbs ~21kg CO2 per year
    trees_needed = max(1, round(co2_emissions / 21))
    
    # Calculate renewable energy equivalent (kWh)
    # 1 kWh from renewable sources saves roughly 0.5kg CO2 compared to fossil fuels
    renewable_energy = round(co2_emissions * 2)
    
    # Approximate offset cost (USD)
    # Carbon offset programs typically charge $10-15 per ton of CO2 (or $0.01-0.015 per kg)
    offset_cost = round(co2_emissions * 0.012, 2)  # ~$12 per ton
    
    # Generate specific offset suggestions
    suggestions = [
        {
            'name': 'Tree Planting',
            'description': f'Plant {trees_needed} tree{"s" if trees_needed > 1 else ""} to absorb your carbon emissions over one year',
            'cost': round(trees_needed * 4, 2),  # ~$4 per tree planting
            'icon': '🌳',
            'impact': f'Absorbs {co2_emissions:.1f}kg CO₂ per year',
            'details': 'Trees capture carbon dioxide through photosynthesis and store it as biomass'
        },
        {
            'name': 'Renewable Energy',
            'description': f'Fund {renewable_energy} kWh of clean energy projects',
            'cost': round(renewable_energy * 0.015, 2),  # ~$0.015 per kWh
            'icon': '☀️',
            'impact': f'Prevents {co2_emissions:.1f}kg CO₂ from fossil fuels',
            'details': 'Supports wind, solar and hydroelectric power projects that replace fossil fuel energy'
        },
        {
            'name': 'Forest Conservation',
            'description': 'Protect existing forest land from deforestation',
            'cost': round(co2_emissions * 0.01, 2),  # ~$10 per ton
            'icon': '🌲',
            'impact': f'Preserves forests that absorb CO₂',
            'details': 'Helps fund protected areas and supports sustainable forest management'
        }
    ]
    
    # If emissions are very small, adjust the suggestions to be more appropriate
    if co2_emissions < 5:
        small_emission_suggestions = [
            {
                'name': 'Eco Habits',
                'description': 'Adopt eco-friendly daily habits to balance your carbon footprint',
                'cost': 0.00,
                'icon': '🌱',
                'impact': 'Offsets small emissions through daily actions',
                'details': 'Simple acts like using reusable bottles, reducing food waste, and turning off lights'
            }
        ]
        suggestions.append(small_emission_suggestions[0])
    
    # For larger emissions, add more substantial offset options
    if co2_emissions > 20:
        large_emission_suggestions = [
            {
                'name': 'Sustainable Agriculture',
                'description': 'Support climate-friendly farming practices',
                'cost': round(co2_emissions * 0.013, 2),
                'icon': '🌾',
                'impact': f'Reduces emissions from food production',
                'details': 'Funds regenerative agriculture that sequesters carbon in soil'
            }
        ]
        suggestions.append(large_emission_suggestions[0])
    
    return {
        'trees': trees_needed,
        'renewable_energy': renewable_energy,
        'offset_cost': offset_cost,
        'suggestions': suggestions
    }

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
    
    # Calculate carbon offset options
    stats['carbon_offset_options'] = calculate_carbon_offset_options(stats['co2_emissions'])
    
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
