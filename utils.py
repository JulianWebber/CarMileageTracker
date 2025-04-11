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
    
    # Get personalized eco-driving tips
    eco_tip = get_personalized_eco_tips(distance, fuel, category)
    
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
    
    # Add the personalized eco-driving tip if available
    if eco_tip:
        summary_parts.append(f"{eco_tip['icon']} **{eco_tip['title']}**: {eco_tip['description']}")
    # Otherwise add a random fun fact
    else:
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

def get_personalized_eco_tips(distance, fuel_consumption=None, category=None):
    """
    Generate personalized eco-driving tips based on journey data.
    
    Parameters:
    - distance: journey distance in km
    - fuel_consumption: fuel used in liters (optional)
    - category: journey category (e.g., 'Commute', 'Shopping', etc.)
    
    Returns a dictionary with eco tip information
    """
    import random
    
    # Calculate efficiency if we have fuel data
    efficiency = None
    if fuel_consumption and not pd.isna(fuel_consumption) and fuel_consumption > 0 and distance > 0:
        efficiency = distance / fuel_consumption  # km/L
    
    # Basic tips for all journeys
    basic_tips = [
        {
            "title": "Regular Maintenance Matters",
            "description": "A well-maintained vehicle can be up to 10% more fuel-efficient. Schedule regular check-ups for your car.",
            "icon": "🔧",
            "impact": "medium",
            "category": "maintenance"
        },
        {
            "title": "Tire Pressure Check",
            "description": "Properly inflated tires can improve your fuel economy by up to 3% and extend tire life.",
            "icon": "🚗",
            "impact": "medium",
            "category": "maintenance"
        },
        {
            "title": "Remove Excess Weight",
            "description": "Every extra 100 pounds in your vehicle reduces fuel economy by about 1%. Clean out unnecessary items from your trunk!",
            "icon": "⚖️",
            "impact": "low",
            "category": "driving_habit"
        },
        {
            "title": "Smooth Acceleration",
            "description": "Gentle acceleration and braking can improve fuel economy by up to 30% on highways and 5% in the city.",
            "icon": "🚦",
            "impact": "high",
            "category": "driving_habit"
        },
        {
            "title": "Optimal Speed",
            "description": "Most vehicles are most efficient at around 80 km/h. Fuel economy typically decreases rapidly above 90 km/h.",
            "icon": "⏱️",
            "impact": "medium",
            "category": "driving_habit"
        },
        {
            "title": "A/C vs. Windows",
            "description": "At highway speeds, use A/C instead of open windows to reduce drag. In city driving, open windows are more efficient.",
            "icon": "❄️",
            "impact": "low",
            "category": "comfort"
        }
    ]
    
    # Tips for short journeys
    short_journey_tips = [
        {
            "title": "Consider Alternatives",
            "description": "For trips under 5 km, walking, cycling, or electric scooters can be faster, healthier, and eco-friendly alternatives.",
            "icon": "🚲",
            "impact": "high",
            "category": "alternative"
        },
        {
            "title": "Combine Short Trips",
            "description": "Combining multiple short errands into one journey can save fuel as a warm engine is more efficient.",
            "icon": "📋",
            "impact": "medium",
            "category": "planning"
        },
        {
            "title": "Engine Warm-Up",
            "description": "Your car uses more fuel when the engine is cold. For short trips, your engine may never reach optimal temperature.",
            "icon": "🔥",
            "impact": "medium",
            "category": "efficiency"
        }
    ]
    
    # Tips for medium to long journeys
    long_journey_tips = [
        {
            "title": "Cruise Control on Highways",
            "description": "Using cruise control on highways can save up to 6% on fuel by maintaining a steady speed.",
            "icon": "🛣️",
            "impact": "medium",
            "category": "driving_habit"
        },
        {
            "title": "Plan Your Route",
            "description": "Use navigation apps to avoid traffic congestion and find the most fuel-efficient route to your destination.",
            "icon": "🗺️",
            "impact": "medium",
            "category": "planning"
        },
        {
            "title": "Pack Lighter",
            "description": "For long trips, pack only what you need. Every extra kg reduces your fuel efficiency.",
            "icon": "🧳",
            "impact": "low",
            "category": "planning"
        },
        {
            "title": "Check Your Roof Rack",
            "description": "A roof rack or carrier creates drag and can decrease fuel economy by up to 25%. Remove when not in use.",
            "icon": "🔝",
            "impact": "high",
            "category": "aerodynamics"
        }
    ]
    
    # Tips for low efficiency journeys
    low_efficiency_tips = [
        {
            "title": "Aggressive Driving Costs",
            "description": "Speeding, rapid acceleration, and hard braking can lower gas mileage by 15-30% on highways and 10-40% in stop-and-go traffic.",
            "icon": "🚨",
            "impact": "high",
            "category": "driving_habit"
        },
        {
            "title": "Engine Check-Up",
            "description": "If your fuel efficiency is consistently low, consider a diagnostic check. A problematic oxygen sensor can reduce efficiency by up to 40%.",
            "icon": "🔍",
            "impact": "high",
            "category": "maintenance"
        },
        {
            "title": "Air Filter Replacement",
            "description": "A clogged air filter can reduce fuel economy by up to 10%. It's an easy and inexpensive fix!",
            "icon": "💨",
            "impact": "medium",
            "category": "maintenance"
        }
    ]
    
    # Category-specific tips
    commute_tips = [
        {
            "title": "Consider Carpooling",
            "description": "Sharing your commute with coworkers can dramatically reduce your carbon footprint and save on fuel costs.",
            "icon": "👥",
            "impact": "high",
            "category": "alternative"
        },
        {
            "title": "Flexible Work Hours",
            "description": "If possible, adjust your work schedule to avoid rush hour traffic for a more fuel-efficient commute.",
            "icon": "⏰",
            "impact": "medium",
            "category": "planning"
        }
    ]
    
    shopping_tips = [
        {
            "title": "Plan Multiple Stops",
            "description": "Plan your shopping trips to hit multiple stores in one journey, starting with the farthest location.",
            "icon": "🛍️",
            "impact": "medium",
            "category": "planning"
        },
        {
            "title": "Online Shopping Alternative",
            "description": "Consider online shopping for bulky or heavy items. Delivery trucks are often more efficient than individual car trips.",
            "icon": "🖥️",
            "impact": "low",
            "category": "alternative"
        }
    ]
    
    # Eligible tips based on journey data
    eligible_tips = basic_tips.copy()
    
    # Add distance-based tips
    if distance < 5:
        eligible_tips.extend(short_journey_tips)
    elif distance > 20:
        eligible_tips.extend(long_journey_tips)
    
    # Add efficiency-based tips
    if efficiency is not None and efficiency < 10:
        eligible_tips.extend(low_efficiency_tips)
    
    # Add category-specific tips
    if category == 'Commute':
        eligible_tips.extend(commute_tips)
    elif category == 'Shopping':
        eligible_tips.extend(shopping_tips)
    
    # Randomly select a tip from eligible ones
    selected_tip = random.choice(eligible_tips)
    
    return selected_tip


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

def generate_route_optimization_suggestions(journey_data):
    """
    Generate route optimization suggestions based on journey patterns.
    
    Parameters:
    - journey_data: DataFrame with journey information
    
    Returns a list of route optimization suggestions
    """
    if journey_data.empty or len(journey_data) < 3:
        return []
    
    suggestions = []
    
    # Look for frequent destinations (more than 1 visit)
    if 'Purpose' in journey_data.columns:
        purpose_counts = journey_data['Purpose'].value_counts()
        frequent_purposes = purpose_counts[purpose_counts > 1].index.tolist()
        
        if frequent_purposes:
            # Find the most efficient journey to each frequent destination
            for purpose in frequent_purposes[:3]:  # Limit to top 3 frequent destinations
                purpose_journeys = journey_data[journey_data['Purpose'] == purpose]
                
                if 'Fuel_Consumption' in purpose_journeys.columns and not purpose_journeys['Fuel_Consumption'].isna().all():
                    # Calculate efficiency for each journey to this destination
                    purpose_journeys['Efficiency'] = purpose_journeys.apply(
                        lambda row: row['Distance'] / row['Fuel_Consumption'] if row['Fuel_Consumption'] > 0 else 0, 
                        axis=1
                    )
                    
                    # Get the most efficient journey
                    most_efficient = purpose_journeys.loc[purpose_journeys['Efficiency'].idxmax()]
                    avg_efficiency = purpose_journeys['Efficiency'].mean()
                    
                    # If the most efficient journey is significantly better than average
                    if most_efficient['Efficiency'] > (avg_efficiency * 1.1) and most_efficient['Efficiency'] > 0:
                        suggestions.append({
                            'title': f"Optimize routes to {purpose}",
                            'description': f"Your most efficient journey to {purpose} used {most_efficient['Efficiency']:.1f} km/L, " +
                                          f"which is {((most_efficient['Efficiency']/avg_efficiency)-1)*100:.0f}% better than your average. " +
                                          f"Consider taking this route more often.",
                            'savings': f"{((most_efficient['Efficiency']/avg_efficiency)-1)*100:.0f}% fuel savings",
                            'icon': '🗺️'
                        })
    
    # Look for similar distance journeys that could be combined
    if 'Date' in journey_data.columns:
        journey_data['Date'] = pd.to_datetime(journey_data['Date'])
        journey_data['Day'] = journey_data['Date'].dt.day_name()
        
        # Group by day of week
        day_groups = journey_data.groupby('Day')
        
        for day, day_journeys in day_groups:
            if len(day_journeys) > 1:
                # Check if there are journeys on the same day that could be combined
                day_journeys = day_journeys.sort_values('Date')
                
                for i in range(len(day_journeys) - 1):
                    j1 = day_journeys.iloc[i]
                    j2 = day_journeys.iloc[i+1]
                    
                    # If journeys are typically done on the same day within a few hours
                    time_diff = (j2['Date'] - j1['Date']).total_seconds() / 3600
                    
                    if 1 < time_diff < 5:  # Between 1 and 5 hours apart
                        suggestions.append({
                            'title': f"Combine {j1['Purpose']} and {j2['Purpose']} trips",
                            'description': f"You often do these journeys on the same {day} within {time_diff:.1f} hours. " +
                                          f"Combining them could save fuel and reduce emissions.",
                            'savings': "Potential 15-20% fuel savings",
                            'icon': '📋'
                        })
                        break  # Just suggest one combination per day
    
    # Add general route optimization tips if specific ones couldn't be generated
    if not suggestions:
        general_tips = [
            {
                'title': "Plan multi-stop journeys efficiently",
                'description': "When running multiple errands, plan your route to minimize backtracking. Start with the farthest destination and work your way back.",
                'savings': "Up to 10-15% distance reduction",
                'icon': '📍'
            },
            {
                'title': "Use navigation apps to avoid traffic",
                'description': "Traffic congestion significantly increases fuel consumption. Use real-time navigation to find less congested routes.",
                'savings': "5-10% fuel savings in urban areas",
                'icon': '📱'
            },
            {
                'title': "Optimize your commute timing",
                'description': "If possible, adjust your travel times to avoid peak traffic hours. Even 30 minutes can make a significant difference.",
                'savings': "Up to 15% fuel savings",
                'icon': '⏰'
            }
        ]
        suggestions.extend(general_tips[:2])  # Add a couple of general tips
    
    return suggestions

def analyze_driving_patterns(df):
    """
    Analyze driving patterns to provide eco-driving insights.
    
    Parameters:
    - df: DataFrame with journey information
    
    Returns a dictionary with driving pattern analysis
    """
    if df.empty or len(df) < 3:
        return {}
    
    # Initialize analysis results
    analysis = {
        'efficiency_trend': 'neutral',
        'efficiency_data': [],
        'patterns': [],
        'recommendations': [],
        'eco_score': 0,
        'improvement_potential': 0,
        'best_practices': [],
        'areas_to_improve': []
    }
    
    # Check if we have enough fuel consumption data
    if 'Fuel_Consumption' in df.columns and not df['Fuel_Consumption'].isna().all():
        # Calculate efficiency for each journey
        df_with_fuel = df[df['Fuel_Consumption'].notna() & (df['Fuel_Consumption'] > 0)]
        if not df_with_fuel.empty:
            df_with_fuel = df_with_fuel.copy()
            df_with_fuel['Efficiency'] = df_with_fuel['Distance'] / df_with_fuel['Fuel_Consumption']
            df_with_fuel = df_with_fuel.sort_values('Date')
            
            # Get efficiency values
            efficiencies = df_with_fuel['Efficiency'].tolist()
            
            # Store efficiency data for visualization
            analysis['efficiency_data'] = [
                {
                    'date': row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else str(row['Date']),
                    'efficiency': row['Efficiency'],
                    'distance': row['Distance'],
                    'purpose': row['Purpose']
                }
                for _, row in df_with_fuel.iterrows()
            ]
            
            # Check for efficiency trend
            if len(efficiencies) >= 3:
                # Simple trend analysis
                first_half = efficiencies[:len(efficiencies)//2]
                second_half = efficiencies[len(efficiencies)//2:]
                
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                if second_avg > first_avg * 1.05:
                    analysis['efficiency_trend'] = 'improving'
                    analysis['patterns'].append({
                        'type': 'positive',
                        'description': 'Your fuel efficiency is improving over time! Recent journeys show better km/L values.',
                        'icon': '📈'
                    })
                elif second_avg < first_avg * 0.95:
                    analysis['efficiency_trend'] = 'declining'
                    analysis['patterns'].append({
                        'type': 'negative',
                        'description': 'Your fuel efficiency has been declining recently. Check for maintenance issues or driving habit changes.',
                        'icon': '📉'
                    })
                else:
                    analysis['efficiency_trend'] = 'stable'
                    analysis['patterns'].append({
                        'type': 'neutral',
                        'description': 'Your fuel efficiency has been relatively stable over time.',
                        'icon': '📊'
                    })
            
            # Analyze variation in efficiency
            if len(efficiencies) >= 3:
                avg_efficiency = sum(efficiencies) / len(efficiencies)
                max_efficiency = max(efficiencies)
                min_efficiency = min(efficiencies)
                variation = (max_efficiency - min_efficiency) / avg_efficiency
                
                if variation > 0.3:  # More than 30% variation
                    analysis['patterns'].append({
                        'type': 'insight',
                        'description': f'Your fuel efficiency varies significantly (up to {variation*100:.0f}%) between journeys. Consistent driving habits could help stabilize this.',
                        'icon': '🔄'
                    })
                    
                    # Find the most efficient journey
                    most_efficient_idx = efficiencies.index(max_efficiency)
                    most_efficient_journey = df_with_fuel.iloc[most_efficient_idx]
                    
                    analysis['recommendations'].append({
                        'title': 'Replicate Your Best Efficiency',
                        'description': f'Your journey on {most_efficient_journey["Date"]} achieved {max_efficiency:.1f} km/L. Try to remember your driving style that day.',
                        'impact': 'high'
                    })
            
            # Calculate eco score (0-100)
            avg_efficiency = sum(efficiencies) / len(efficiencies)
            # Score scale: 10 km/L = 50 points, 20 km/L = 100 points
            eco_score = min(100, max(0, 50 + (avg_efficiency - 10) * 5))
            analysis['eco_score'] = round(eco_score)
            
            # Calculate improvement potential
            best_efficiency = max(efficiencies)
            if best_efficiency > avg_efficiency:
                potential_improvement = ((best_efficiency / avg_efficiency) - 1) * 100
                analysis['improvement_potential'] = round(potential_improvement)
                
                # If significant improvement potential exists
                if potential_improvement > 10:
                    analysis['recommendations'].append({
                        'title': 'Potential Efficiency Improvement',
                        'description': f'You could improve your average efficiency by up to {potential_improvement:.0f}% based on your best recorded journey.',
                        'impact': 'high'
                    })
            
            # Identify good and bad driving patterns
            df_with_fuel['Category'] = df_with_fuel['Category'].fillna('Other')
            
            # Analyze by category if we have category data
            if 'Category' in df_with_fuel.columns:
                category_efficiencies = df_with_fuel.groupby('Category')['Efficiency'].mean().to_dict()
                
                # Find best and worst performing categories
                if len(category_efficiencies) > 1:
                    best_category = max(category_efficiencies.items(), key=lambda x: x[1])
                    worst_category = min(category_efficiencies.items(), key=lambda x: x[1])
                    
                    if best_category[1] > worst_category[1] * 1.15:  # At least 15% difference
                        analysis['patterns'].append({
                            'type': 'insight',
                            'description': f'Your {best_category[0]} journeys are {((best_category[1]/worst_category[1])-1)*100:.0f}% more fuel-efficient than your {worst_category[0]} journeys.',
                            'icon': '🔍'
                        })
            
            # Analyze short trips efficiency
            short_trips = df_with_fuel[df_with_fuel['Distance'] < 5]
            long_trips = df_with_fuel[df_with_fuel['Distance'] >= 5]
            
            if not short_trips.empty and not long_trips.empty:
                short_efficiency = short_trips['Efficiency'].mean()
                long_efficiency = long_trips['Efficiency'].mean()
                
                if short_efficiency < long_efficiency * 0.85:  # Short trips at least 15% less efficient
                    analysis['patterns'].append({
                        'type': 'negative',
                        'description': 'Your short trips (under 5km) are significantly less fuel-efficient. Consider combining these errands when possible.',
                        'icon': '🔄'
                    })
                    
                    analysis['recommendations'].append({
                        'title': 'Combine Short Trips',
                        'description': 'Short journeys with cold engines use up to 40% more fuel. Try combining multiple errands into single trips.',
                        'impact': 'medium'
                    })
            
            # Build best practices list
            if avg_efficiency > 12:
                analysis['best_practices'].append({
                    'title': 'Steady Driving',
                    'description': 'You maintain good overall efficiency, likely through steady speeds and gentle acceleration.',
                    'icon': '🚗'
                })
            
            if analysis['efficiency_trend'] == 'improving':
                analysis['best_practices'].append({
                    'title': 'Continuous Improvement',
                    'description': 'You\'re consistently improving your efficiency, showing adaptive driving habits.',
                    'icon': '📈'
                })
            
            # Build areas to improve
            if avg_efficiency < 10:
                analysis['areas_to_improve'].append({
                    'title': 'Overall Efficiency',
                    'description': 'Your average fuel economy is below optimal levels. Focus on steady acceleration and maintaining constant speeds.',
                    'icon': '⚠️'
                })
            
            if variation > 0.3:
                analysis['areas_to_improve'].append({
                    'title': 'Consistency',
                    'description': 'Your efficiency varies significantly between journeys. Try to develop more consistent driving habits.',
                    'icon': '📊'
                })
    
    # Add some general recommendations if we don't have enough specific ones
    if len(analysis['recommendations']) < 2:
        general_recommendations = [
            {
                'title': 'Anticipate Traffic Flow',
                'description': 'Look ahead and anticipate stops to reduce unnecessary braking and acceleration.',
                'impact': 'medium'
            },
            {
                'title': 'Regular Vehicle Maintenance',
                'description': 'Keep your vehicle well-maintained with regular oil changes and air filter replacements.',
                'impact': 'medium'
            },
            {
                'title': 'Optimal Highway Speed',
                'description': 'Most vehicles achieve optimal fuel efficiency between 75-85 km/h on highways.',
                'impact': 'high'
            }
        ]
        
        # Add general recommendations to fill up to at least 3
        needed = max(0, 3 - len(analysis['recommendations']))
        analysis['recommendations'].extend(general_recommendations[:needed])
    
    return analysis

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
    
    # Generate route optimization suggestions
    stats['route_optimization'] = generate_route_optimization_suggestions(df)
    
    # Analyze driving patterns
    stats['driving_patterns'] = analyze_driving_patterns(df)
    
    return stats
