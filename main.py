import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os
import utils
from utils import (
    load_data, save_data, calculate_statistics, validate_input, 
    generate_journey_summary, generate_weekly_eco_challenges, 
    update_eco_challenge_progress, generate_leaderboard_data
)

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
if 'carbon_offsets' not in st.session_state:
    st.session_state.carbon_offsets = []
if 'offset_selected' not in st.session_state:
    st.session_state.offset_selected = None
if 'offset_amount' not in st.session_state:
    st.session_state.offset_amount = 0
if 'total_offset' not in st.session_state:
    st.session_state.total_offset = 0
if 'show_achievement' not in st.session_state:
    st.session_state.show_achievement = False
if 'achievements' not in st.session_state:
    st.session_state.achievements = []
if 'eco_tips_shown' not in st.session_state:
    st.session_state.eco_tips_shown = []
if 'sustainability_challenges' not in st.session_state:
    st.session_state.sustainability_challenges = []
if 'active_challenge' not in st.session_state:
    st.session_state.active_challenge = None
if 'impact_milestones' not in st.session_state:
    # Track environmental impact milestones
    st.session_state.impact_milestones = {
        'trees_planted': 0,
        'co2_offset': 0,
        'offset_actions': 0,
        'badges_earned': []
    }

def update_impact_milestones(offset_option, co2_emissions):
    """Update the environmental impact milestones based on the offset action"""
    # Update CO2 offset total
    st.session_state.impact_milestones['co2_offset'] += co2_emissions
    
    # Update offset actions count
    st.session_state.impact_milestones['offset_actions'] += 1
    
    # Update trees planted if applicable
    if 'Tree' in offset_option['name']:
        st.session_state.impact_milestones['trees_planted'] += 1
    
    # Check for new badges
    current_badges = st.session_state.impact_milestones['badges_earned']
    
    # First offset badge
    if st.session_state.impact_milestones['offset_actions'] == 1 and 'first_offset' not in current_badges:
        st.session_state.impact_milestones['badges_earned'].append('first_offset')
        st.session_state.achievements.append({
            'badge': 'first_offset',
            'title': 'Carbon Conscious',
            'description': 'Completed your first carbon offset! 🌱',
            'icon': '🌱',
            'date': datetime.datetime.now().strftime('%Y-%m-%d')
        })
        st.session_state.show_achievement = True
    
    # Tree planter badge
    if st.session_state.impact_milestones['trees_planted'] >= 5 and 'tree_planter' not in current_badges:
        st.session_state.impact_milestones['badges_earned'].append('tree_planter')
        st.session_state.achievements.append({
            'badge': 'tree_planter',
            'title': 'Tree Planter',
            'description': 'Contributed to planting 5 trees! The forest thanks you. 🌳',
            'icon': '🌳',
            'date': datetime.datetime.now().strftime('%Y-%m-%d')
        })
        st.session_state.show_achievement = True
    
    # Climate champion badge
    if st.session_state.impact_milestones['co2_offset'] >= 50 and 'climate_champion' not in current_badges:
        st.session_state.impact_milestones['badges_earned'].append('climate_champion')
        st.session_state.achievements.append({
            'badge': 'climate_champion',
            'title': 'Climate Champion',
            'description': 'Offset over 50kg of CO₂! You\'re making a real difference. 🌍',
            'icon': '🌍',
            'date': datetime.datetime.now().strftime('%Y-%m-%d')
        })
        st.session_state.show_achievement = True
    
    # Super offsetter badge
    if st.session_state.impact_milestones['offset_actions'] >= 10 and 'super_offsetter' not in current_badges:
        st.session_state.impact_milestones['badges_earned'].append('super_offsetter')
        st.session_state.achievements.append({
            'badge': 'super_offsetter',
            'title': 'Super Offsetter',
            'description': 'Completed 10 carbon offset actions! You\'re on a green streak! 💚',
            'icon': '💚',
            'date': datetime.datetime.now().strftime('%Y-%m-%d')
        })
        st.session_state.show_achievement = True

def check_achievements():
    """Check and display achievements if there are any new ones"""
    if st.session_state.show_achievement and st.session_state.achievements:
        # Get the most recent achievement
        achievement = st.session_state.achievements[-1]
        
        # Display the achievement popup
        st.markdown("""
        <style>
        @keyframes achievementAppear {
            0% { transform: translateY(100px); opacity: 0; }
            10% { transform: translateY(0); opacity: 1; }
            90% { transform: translateY(0); opacity: 1; }
            100% { transform: translateY(100px); opacity: 0; }
        }
        
        @keyframes achievementShine {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        
        @keyframes achievementIconPulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }
        
        @keyframes achievementConfetti {
            0% { background-position: 0% 0%; }
            100% { background-position: 100% 100%; }
        }
        
        .achievement-popup {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #4CAF50, #2E7D32);
            color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            text-align: center;
            width: 300px;
            animation: achievementAppear 4s forwards;
        }
        
        .achievement-popup::before {
            content: "";
            position: absolute;
            top: -3px;
            left: -3px;
            right: -3px;
            bottom: -3px;
            z-index: -1;
            background: linear-gradient(90deg, #ffd700, #ffec80, #ffd700);
            background-size: 200% auto;
            border-radius: 18px;
            animation: achievementShine 3s linear infinite;
        }
        
        .achievement-icon {
            font-size: 3rem;
            margin: 10px 0;
            display: inline-block;
            animation: achievementIconPulse 2s infinite;
        }
        
        .achievement-title {
            font-size: 1.3rem;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .achievement-description {
            font-size: 0.9rem;
            margin-bottom: 10px;
        }
        
        .achievement-confetti {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M10 10l10 10L10 30l10 10L10 50l10 10L10 70l10 10L10 90l10 10H0V0h20l-10 10zm30 0l10 10L40 30l10 10L40 50l10 10L40 70l10 10L40 90l10 10H30V0h20l-10 10zm30 0l10 10L70 30l10 10L70 50l10 10L70 70l10 10L70 90l10 10H60V0h20l-10 10zm30 0l10 10L100 30l10 10L100 50l10 10L100 70l10 10L100 90l10 10H90V0h20l-10 10z' fill='%23ffffff' fill-opacity='0.1'/%3E%3C/svg%3E");
            background-size: 30px 30px;
            animation: achievementConfetti 10s linear infinite;
            opacity: 0.6;
            border-radius: 15px;
        }
        </style>
        
        <div class="achievement-popup">
            <div class="achievement-confetti"></div>
            <div>ACHIEVEMENT UNLOCKED!</div>
            <div class="achievement-icon">{}</div>
            <div class="achievement-title">{}</div>
            <div class="achievement-description">{}</div>
        </div>
        """.format(achievement['icon'], achievement['title'], achievement['description']), unsafe_allow_html=True)
        
        # Reset the flag
        st.session_state.show_achievement = False

def display_leaderboard(user_points):
    """Display eco-challenge leaderboard with animated rankings"""
    st.markdown("### 🏆 Eco-Leaderboard")
    st.markdown("See how your eco-driving performance compares with others!")
    
    # Generate leaderboard data
    leaderboard = generate_leaderboard_data(user_points)
    
    # Custom CSS for leaderboard
    st.markdown("""
    <style>
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes highlight {
        0% { background-color: rgba(76, 175, 80, 0.3); }
        50% { background-color: rgba(76, 175, 80, 0.1); }
        100% { background-color: rgba(76, 175, 80, 0.3); }
    }
    
    .leaderboard-container {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        overflow: hidden;
        margin: 20px 0;
    }
    
    .leaderboard-header {
        background: linear-gradient(90deg, #1E88E5, #64B5F6);
        color: white;
        padding: 15px 20px;
        font-weight: 500;
        display: flex;
        align-items: center;
    }
    
    .leaderboard-row {
        display: flex;
        align-items: center;
        padding: 12px 20px;
        border-bottom: 1px solid #f0f0f0;
        animation: fadeInUp 0.5s ease forwards;
        animation-delay: calc(var(--row-index) * 0.1s);
        opacity: 0;
    }
    
    .leaderboard-row.current-user {
        background-color: rgba(76, 175, 80, 0.1);
        animation: fadeInUp 0.5s ease forwards, highlight 2s ease infinite;
        animation-delay: calc(var(--row-index) * 0.1s), 0.5s;
    }
    
    .rank {
        flex: 0 0 50px;
        font-weight: 700;
        font-size: 1.1rem;
        color: #333;
    }
    
    .rank-1 {
        color: #FFD700;
    }
    
    .rank-2 {
        color: #C0C0C0;
    }
    
    .rank-3 {
        color: #CD7F32;
    }
    
    .avatar {
        flex: 0 0 40px;
        font-size: 1.5rem;
        text-align: center;
    }
    
    .user-info {
        flex: 1;
        padding: 0 15px;
    }
    
    .username {
        font-weight: 500;
        color: #333;
    }
    
    .level-indicator {
        font-size: 0.8rem;
        color: #666;
        margin-top: 3px;
    }
    
    .stats {
        flex: 0 0 100px;
        text-align: right;
        font-weight: 500;
        color: #1E88E5;
    }
    
    .medal {
        margin-left: 10px;
        font-size: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render leaderboard
    st.markdown('<div class="leaderboard-container">', unsafe_allow_html=True)
    st.markdown('<div class="leaderboard-header">Global Eco-Champions</div>', unsafe_allow_html=True)
    
    for i, entry in enumerate(leaderboard):
        medal = ""
        rank_class = ""
        
        if entry['rank'] == 1:
            medal = "🥇"
            rank_class = "rank-1"
        elif entry['rank'] == 2:
            medal = "🥈"
            rank_class = "rank-2"
        elif entry['rank'] == 3:
            medal = "🥉"
            rank_class = "rank-3"
        
        user_class = "current-user" if entry['is_current_user'] else ""
        
        st.markdown(f"""
        <div class="leaderboard-row {user_class}" style="--row-index: {i}">
            <div class="rank {rank_class}">{entry['rank']}</div>
            <div class="avatar">{entry['avatar']}</div>
            <div class="user-info">
                <div class="username">{entry['username']}{' (YOU)' if entry['is_current_user'] else ''}</div>
                <div class="level-indicator">Level {entry['level']} • {entry['challenges_completed']} challenges</div>
            </div>
            <div class="stats">{entry['points']} pts</div>
            <div class="medal">{medal}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tips to improve ranking
    st.markdown("### 💡 Tips to Climb the Ranks")
    
    tips_cols = st.columns(3)
    
    tips = [
        {"icon": "🔄", "title": "Daily Consistency", "text": "Log your journeys regularly and complete daily challenges to earn steady points."},
        {"icon": "🎯", "title": "Focus on Challenges", "text": "Prioritize the highest-point challenges each week for maximum gains."},
        {"icon": "🌱", "title": "Offset Actions", "text": "Carbon offset actions earn bonus points and special achievements."}
    ]
    
    for i, tip in enumerate(tips):
        with tips_cols[i]:
            st.markdown(f"""
            <div style='
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                padding: 15px;
                text-align: center;
                height: 100%;
            '>
                <div style='font-size: 2rem; margin-bottom: 10px;'>{tip["icon"]}</div>
                <div style='font-weight: 500; margin-bottom: 10px;'>{tip["title"]}</div>
                <div style='font-size: 0.9rem; color: #666;'>{tip["text"]}</div>
            </div>
            """, unsafe_allow_html=True)

def display_driving_patterns_analysis(stats):
    """Display detailed analysis of driving patterns with interactive visualizations"""
    if (not stats or 'driving_patterns' not in stats or not stats['driving_patterns'] or 
        'efficiency_data' not in stats['driving_patterns'] or not stats['driving_patterns']['efficiency_data']):
        return
    
    patterns = stats['driving_patterns']
    
    st.markdown("<div class='chart-container' style='border-left: 4px solid #FF9800;'>", unsafe_allow_html=True)
    st.markdown("<p class='stats-section-title'>🚗 Eco-Driving Pattern Analysis</p>", unsafe_allow_html=True)
    
    # Add driving pattern analysis styles
    st.markdown("""
    <style>
    @keyframes scoreGauge {
        from { transform: rotate(-120deg); }
        to { transform: rotate(var(--score-angle)); }
    }
    
    @keyframes patternPulse {
        0% { transform: scale(1); opacity: 0.9; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(1); opacity: 0.9; }
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .driving-dashboard {
        display: flex;
        flex-direction: column;
        gap: 20px;
        margin: 20px 0;
    }
    
    .eco-score-container {
        background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
        border-radius: 15px;
        padding: 25px;
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        overflow: hidden;
    }
    
    .gauge-container {
        position: relative;
        width: 180px;
        height: 90px;
        margin: 15px 0;
    }
    
    .gauge-background {
        position: absolute;
        width: 180px;
        height: 90px;
        border-radius: 90px 90px 0 0;
        background: #EEEEEE;
        overflow: hidden;
    }
    
    .gauge-fill {
        position: absolute;
        width: 180px;
        height: 90px;
        border-radius: 90px 90px 0 0;
        background: conic-gradient(
            from 180deg,
            #F44336 0deg 60deg,
            #FFC107 60deg 120deg,
            #4CAF50 120deg 180deg
        );
        transform-origin: center bottom;
        transform: rotate(-120deg);
        animation: scoreGauge 1.5s ease-out forwards;
    }
    
    .gauge-center {
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 150px;
        height: 75px;
        border-radius: 75px 75px 0 0;
        background: white;
    }
    
    .gauge-value {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.8rem;
        font-weight: 700;
        color: #FF9800;
    }
    
    .gauge-label {
        font-size: 1rem;
        font-weight: 500;
        color: #555;
        margin-top: 15px;
        text-align: center;
    }
    
    .improvement-badge {
        position: absolute;
        top: 15px;
        right: 15px;
        background-color: #FF9800;
        color: white;
        font-size: 0.9rem;
        font-weight: 500;
        padding: 5px 12px;
        border-radius: 20px;
    }
    
    .patterns-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    
    .pattern-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
        display: flex;
        align-items: flex-start;
        gap: 15px;
        overflow: hidden;
        position: relative;
    }
    
    .pattern-card.positive {
        border-left: 4px solid #4CAF50;
    }
    
    .pattern-card.negative {
        border-left: 4px solid #F44336;
    }
    
    .pattern-card.neutral {
        border-left: 4px solid #9E9E9E;
    }
    
    .pattern-card.insight {
        border-left: 4px solid #2196F3;
    }
    
    .pattern-icon {
        font-size: 2.2rem;
        animation: patternPulse 3s infinite ease-in-out;
    }
    
    .pattern-card.positive .pattern-icon {
        color: #4CAF50;
    }
    
    .pattern-card.negative .pattern-icon {
        color: #F44336;
    }
    
    .pattern-card.neutral .pattern-icon {
        color: #9E9E9E;
    }
    
    .pattern-card.insight .pattern-icon {
        color: #2196F3;
    }
    
    .pattern-content {
        flex: 1;
    }
    
    .pattern-description {
        color: #555;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    
    .recommendations-container {
        margin-top: 25px;
    }
    
    .recommendation-title {
        font-weight: 600;
        color: #FF9800;
        font-size: 1.1rem;
        margin-bottom: 15px;
    }
    
    .recommendation-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    
    .recommendation-item {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        padding: 15px;
        border-radius: 12px;
        position: relative;
    }
    
    .recommendation-item.high {
        border-left: 4px solid #F57C00;
    }
    
    .recommendation-item.medium {
        border-left: 4px solid #FB8C00;
    }
    
    .recommendation-item.low {
        border-left: 4px solid #FFB74D;
    }
    
    .recommendation-header {
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
    }
    
    .recommendation-text {
        color: #555;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    .impact-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .impact-badge.high {
        background-color: #F57C00;
        color: white;
    }
    
    .impact-badge.medium {
        background-color: #FB8C00;
        color: white;
    }
    
    .impact-badge.low {
        background-color: #FFB74D;
        color: white;
    }
    
    .practices-container {
        margin-top: 25px;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
    }
    
    .practices-column {
        flex: 1;
    }
    
    .practices-title {
        font-weight: 600;
        font-size: 1.05rem;
        margin-bottom: 12px;
    }
    
    .best-practices .practices-title {
        color: #2E7D32;
    }
    
    .areas-improve .practices-title {
        color: #D32F2F;
    }
    
    .practice-card {
        background: white;
        padding: 12px 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    
    .best-practices .practice-card {
        border-left: 3px solid #4CAF50;
    }
    
    .areas-improve .practice-card {
        border-left: 3px solid #F44336;
    }
    
    .practice-icon {
        font-size: 1.5rem;
    }
    
    .best-practices .practice-icon {
        color: #4CAF50;
    }
    
    .areas-improve .practice-icon {
        color: #F44336;
    }
    
    .practice-content {
        flex: 1;
    }
    
    .practice-title {
        font-weight: 500;
        color: #333;
        margin-bottom: 5px;
        font-size: 0.95rem;
    }
    
    .practice-description {
        color: #666;
        font-size: 0.85rem;
        line-height: 1.3;
    }
    </style>
    
    <div class="driving-dashboard">
    """, unsafe_allow_html=True)
    
    # Display Eco-Score gauge
    eco_score = patterns.get('eco_score', 50)
    improvement = patterns.get('improvement_potential', 0)
    
    # Calculate gauge angle: 
    # - 0 score = -120deg (left side of gauge)
    # - 100 score = 60deg (right side of gauge)
    # Total range is 180deg
    score_angle = -120 + (eco_score * 180 / 100)
    
    st.markdown(f"""
    <div class="eco-score-container">
        <h3 style="margin: 0; color: #FF9800; font-size: 1.3rem;">Your Eco-Driving Score</h3>
        <div class="gauge-container">
            <div class="gauge-background"></div>
            <div class="gauge-fill" style="--score-angle: {score_angle}deg;"></div>
            <div class="gauge-center"></div>
            <div class="gauge-value">{eco_score}</div>
        </div>
        <div class="gauge-label">Based on your driving efficiency data</div>
        
        {f'<div class="improvement-badge">⬆️ {improvement}% improvement potential</div>' if improvement > 0 else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # Display driving patterns
    if patterns.get('patterns'):
        st.markdown("<h3 style='margin: 25px 0 15px; color: #FF9800; font-size: 1.2rem;'>Driving Pattern Insights</h3>", unsafe_allow_html=True)
        st.markdown("<div class='patterns-grid'>", unsafe_allow_html=True)
        
        for pattern in patterns['patterns']:
            pattern_type = pattern.get('type', 'neutral')
            st.markdown(f"""
            <div class="pattern-card {pattern_type}">
                <div class="pattern-icon">{pattern['icon']}</div>
                <div class="pattern-content">
                    <div class="pattern-description">{pattern['description']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display recommendations
    if patterns.get('recommendations'):
        st.markdown("<div class='recommendations-container'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin: 0 0 15px; color: #FF9800; font-size: 1.2rem;'>Personalized Recommendations</h3>", unsafe_allow_html=True)
        st.markdown("<div class='recommendation-list'>", unsafe_allow_html=True)
        
        for rec in patterns['recommendations']:
            impact = rec.get('impact', 'medium')
            st.markdown(f"""
            <div class="recommendation-item {impact}">
                <div class="recommendation-header">{rec['title']}</div>
                <div class="recommendation-text">{rec['description']}</div>
                <div class="impact-badge {impact}">{impact.capitalize()} Impact</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display best practices and areas to improve
    if patterns.get('best_practices') or patterns.get('areas_to_improve'):
        st.markdown("<div class='practices-container'>", unsafe_allow_html=True)
        
        # Best practices column
        if patterns.get('best_practices'):
            st.markdown("<div class='practices-column best-practices'>", unsafe_allow_html=True)
            st.markdown("<div class='practices-title'>💯 Your Best Practices</div>", unsafe_allow_html=True)
            
            for practice in patterns['best_practices']:
                st.markdown(f"""
                <div class="practice-card">
                    <div class="practice-icon">{practice['icon']}</div>
                    <div class="practice-content">
                        <div class="practice-title">{practice['title']}</div>
                        <div class="practice-description">{practice['description']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Areas to improve column
        if patterns.get('areas_to_improve'):
            st.markdown("<div class='practices-column areas-improve'>", unsafe_allow_html=True)
            st.markdown("<div class='practices-title'>🔍 Areas to Improve</div>", unsafe_allow_html=True)
            
            for area in patterns['areas_to_improve']:
                st.markdown(f"""
                <div class="practice-card">
                    <div class="practice-icon">{area['icon']}</div>
                    <div class="practice-content">
                        <div class="practice-title">{area['title']}</div>
                        <div class="practice-description">{area['description']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display efficiency trend visualization
    if patterns.get('efficiency_data') and len(patterns['efficiency_data']) >= 3:
        st.markdown("<h3 style='margin: 30px 0 15px; color: #FF9800; font-size: 1.2rem;'>Fuel Efficiency Trend</h3>", unsafe_allow_html=True)
        
        # Convert data to DataFrame for Plotly
        efficiency_data = patterns['efficiency_data']
        efficiency_df = pd.DataFrame(efficiency_data)
        efficiency_df['date'] = pd.to_datetime(efficiency_df['date'])
        efficiency_df = efficiency_df.sort_values('date')
        
        # Create line chart
        fig = px.line(
            efficiency_df, 
            x='date', 
            y='efficiency',
            markers=True,
            line_shape='spline',
            hover_data=['purpose', 'distance'],
            labels={
                'date': 'Journey Date',
                'efficiency': 'Fuel Efficiency (km/L)',
                'purpose': 'Purpose',
                'distance': 'Distance (km)'
            },
            title=None
        )
        
        # Customize the chart
        fig.update_traces(line=dict(width=3, color='#FF9800'), marker=dict(size=8, color='#FB8C00'))
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=0, l=0, r=0),
            hovermode='x unified',
            xaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12),
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)'
            ),
            yaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12),
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)',
                zeroline=False
            )
        )
        
        # Add a trend line
        fig.add_traces(
            px.scatter(
                efficiency_df, 
                x='date', 
                y='efficiency', 
                trendline='ols'
            ).data[1]
        )
        fig.data[1].line.color = '#4CAF50'
        fig.data[1].line.dash = 'dash'
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close driving dashboard
    st.markdown("</div>", unsafe_allow_html=True)  # Close chart container

def display_route_optimization(stats):
    """Display route optimization suggestions to reduce fuel usage and emissions"""
    if not stats or stats['total_journeys'] < 3 or 'route_optimization' not in stats or not stats['route_optimization']:
        return
    
    st.markdown("<div class='chart-container' style='border-left: 4px solid #3F51B5;'>", unsafe_allow_html=True)
    st.markdown("<p class='stats-section-title'>🗺️ Smart Route Suggestions</p>", unsafe_allow_html=True)
    
    # Add route optimization card styles
    st.markdown("""
    <style>
    @keyframes mapPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    @keyframes routeAppear {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes shimmerRoute {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    .route-suggestions-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
        margin: 20px 0;
    }
    
    .route-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
        display: flex;
        align-items: flex-start;
        gap: 20px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        animation: routeAppear 0.5s ease-out forwards;
    }
    
    .route-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
    }
    
    .route-card::after {
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        background: linear-gradient(90deg, 
            rgba(255,255,255, 0) 0%, 
            rgba(255,255,255, 0.2) 25%, 
            rgba(255,255,255, 0.2) 50%, 
            rgba(255,255,255, 0) 100%);
        background-size: 200% 100%;
        pointer-events: none;
        animation: shimmerRoute 3s infinite;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .route-card:hover::after {
        opacity: 1;
    }
    
    .route-icon {
        font-size: 2.5rem;
        animation: mapPulse 3s infinite ease;
        color: #3F51B5;
    }
    
    .route-content {
        flex: 1;
    }
    
    .route-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: #3F51B5;
        margin-bottom: 8px;
    }
    
    .route-description {
        color: #555;
        font-size: 0.9rem;
        margin-bottom: 10px;
        line-height: 1.4;
    }
    
    .route-savings {
        display: inline-block;
        background-color: #E8EAF6;
        color: #3F51B5;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 5px 10px;
        border-radius: 20px;
    }
    </style>
    
    <div class="route-suggestions-container">
    """, unsafe_allow_html=True)
    
    # Display each optimization suggestion
    for suggestion in stats['route_optimization']:
        st.markdown(f"""
        <div class="route-card">
            <div class="route-icon">{suggestion['icon']}</div>
            <div class="route-content">
                <div class="route-title">{suggestion['title']}</div>
                <div class="route-description">{suggestion['description']}</div>
                <div class="route-savings">💰 {suggestion['savings']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add a note about route optimization benefits
    co2_per_liter = 2.31  # kg of CO2 per liter of gasoline
    potential_savings = 0.15  # 15% potential savings from route optimization
    total_fuel = stats.get('total_fuel', 0)
    
    if total_fuel > 0:
        fuel_saved = total_fuel * potential_savings
        co2_saved = fuel_saved * co2_per_liter
        
        st.markdown(f"""
        <div style="text-align: center; margin-top: 15px; padding: 10px; background-color: #E8EAF6; border-radius: 10px;">
            <p style="margin-bottom: 5px; font-weight: 500; color: #3F51B5;">
                By optimizing your routes, you could potentially save:
            </p>
            <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;">
                <div>
                    <span style="font-size: 1.3rem; font-weight: 600; color: #3F51B5;">{fuel_saved:.1f}L</span>
                    <div style="font-size: 0.9rem; color: #555;">Fuel</div>
                </div>
                <div>
                    <span style="font-size: 1.3rem; font-weight: 600; color: #3F51B5;">${(fuel_saved * stats.get('fuel_price', 1.5)):.2f}</span>
                    <div style="font-size: 0.9rem; color: #555;">Money</div>
                </div>
                <div>
                    <span style="font-size: 1.3rem; font-weight: 600; color: #3F51B5;">{co2_saved:.1f}kg</span>
                    <div style="font-size: 0.9rem; color: #555;">CO₂ Emissions</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close route suggestions container
    st.markdown("</div>", unsafe_allow_html=True)  # Close chart container

def display_sustainability_challenges(stats):
    """Display sustainability challenges and goals for eco-friendly driving"""
    if not stats or stats['total_journeys'] < 2:
        return
    
    st.markdown("<div class='chart-container' style='border-left: 4px solid #8BC34A;'>", unsafe_allow_html=True)
    st.markdown("<p class='stats-section-title'>🌿 Sustainability Challenges</p>", unsafe_allow_html=True)
    
    # Define the challenges CSS
    st.markdown("""
    <style>
    @keyframes growLeaf {
        0% { transform: scale(0.8); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    @keyframes fadeInChallenge {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes progressPulse {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .challenges-container {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-top: 20px;
    }
    
    .challenge-card {
        flex: 1 1 300px;
        background: linear-gradient(135deg, #FFFFFF 0%, #F5F5F5 100%);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
        position: relative;
        transition: all 0.3s ease;
        animation: fadeInChallenge 0.5s ease-out forwards;
        overflow: hidden;
    }
    
    .challenge-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    .challenge-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
        display: inline-block;
        animation: growLeaf 2s ease infinite;
    }
    
    .challenge-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: #2E7D32;
        margin-bottom: 10px;
    }
    
    .challenge-description {
        color: #555;
        font-size: 0.9rem;
        margin-bottom: 15px;
    }
    
    .challenge-progress-container {
        height: 12px;
        background-color: #E0E0E0;
        border-radius: 10px;
        margin: 15px 0;
        overflow: hidden;
    }
    
    .challenge-progress-bar {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #4CAF50, #8BC34A, #4CAF50);
        background-size: 200% 200%;
        animation: progressPulse 3s ease infinite;
        transition: width 1s ease;
    }
    
    .challenge-status {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        color: #555;
    }
    
    .challenge-action-btn {
        margin-top: 15px;
        background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
        border: none;
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-block;
    }
    
    .challenge-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
    }
    
    .challenge-reward {
        position: absolute;
        top: 15px;
        right: 15px;
        background-color: #FFC107;
        color: #603F00;
        font-size: 0.8rem;
        padding: 3px 8px;
        border-radius: 10px;
        font-weight: 500;
    }
    </style>
    
    <div class="challenges-container">
    """, unsafe_allow_html=True)
    
    # Define available challenges based on user stats
    avg_fuel_economy = stats.get('fuel_economy', 0)
    total_distance = stats.get('total_distance', 0)
    total_co2 = stats.get('co2_emissions', 0)
    total_offset = st.session_state.total_offset
    offset_percentage = (total_offset / total_co2 * 100) if total_co2 > 0 else 0
    
    # Fuel efficiency challenge
    if avg_fuel_economy > 0:
        current_efficiency = avg_fuel_economy
        target_efficiency = max(15, current_efficiency * 1.1)  # 10% improvement or at least 15 km/L
        progress_percentage = min(100, (current_efficiency / target_efficiency) * 100)
        
        st.markdown(f"""
        <div class="challenge-card">
            <div class="challenge-reward">Badge: Eco Driver</div>
            <div class="challenge-icon">🚙</div>
            <div class="challenge-title">Fuel Efficiency Master</div>
            <div class="challenge-description">
                Improve your average fuel economy to {target_efficiency:.1f} km/L. 
                Currently at {current_efficiency:.1f} km/L.
            </div>
            <div class="challenge-progress-container">
                <div class="challenge-progress-bar" style="width: {progress_percentage}%;"></div>
            </div>
            <div class="challenge-status">
                <span>{current_efficiency:.1f} km/L</span>
                <span>{target_efficiency:.1f} km/L</span>
            </div>
            <div class="challenge-description">
                <b>Tips:</b> Maintain steady speeds, avoid rapid acceleration, and check tire pressure.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Carbon offset challenge
    if total_co2 > 0:
        st.markdown(f"""
        <div class="challenge-card">
            <div class="challenge-reward">Badge: Carbon Neutralizer</div>
            <div class="challenge-icon">🌍</div>
            <div class="challenge-title">Carbon Neutral Driver</div>
            <div class="challenge-description">
                Offset 100% of your carbon emissions through green actions.
                Currently offset: {offset_percentage:.1f}% of your {total_co2:.1f}kg CO₂.
            </div>
            <div class="challenge-progress-container">
                <div class="challenge-progress-bar" style="width: {offset_percentage}%;"></div>
            </div>
            <div class="challenge-status">
                <span>{total_offset:.1f}kg</span>
                <span>{total_co2:.1f}kg</span>
            </div>
            <div class="challenge-description">
                <b>How:</b> Use the carbon offset options in the statistics page to balance your carbon footprint.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Consistent eco-driver challenge
    if stats['total_journeys'] >= 3:
        st.markdown(f"""
        <div class="challenge-card">
            <div class="challenge-reward">Badge: Eco Streak</div>
            <div class="challenge-icon">📊</div>
            <div class="challenge-title">Eco-Driving Streak</div>
            <div class="challenge-description">
                Maintain fuel efficiency above 10 km/L for 5 consecutive journeys.
            </div>
            <div class="challenge-progress-container">
                <div class="challenge-progress-bar" style="width: 20%;"></div>
            </div>
            <div class="challenge-status">
                <span>1/5 journeys</span>
                <span>Goal: 5</span>
            </div>
            <div class="challenge-description">
                <b>Reward:</b> Unlock detailed efficiency analytics dashboard.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close challenges container
    
    # Add a tree growth visualization based on offsets
    trees_planted = st.session_state.impact_milestones['trees_planted']
    if trees_planted > 0:
        st.markdown("<p class='stats-section-title' style='margin-top: 25px;'>🌳 Your Forest Growth</p>", unsafe_allow_html=True)
        
        st.markdown("""
        <style>
        @keyframes treeGrow {
            0% { transform: scale(0.9); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .forest-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
            padding: 20px;
            background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
            border-radius: 15px;
        }
        
        .tree {
            font-size: 3rem;
            animation: treeGrow 3s ease infinite;
            animation-delay: calc(var(--i) * 0.5s);
        }
        </style>
        
        <div class="forest-container">
        """, unsafe_allow_html=True)
        
        # Display trees with staggered animations
        for i in range(min(15, trees_planted)):  # Limit to 15 trees to avoid overcrowding
            tree_size = 3 + (i % 4) * 0.5  # Vary tree sizes
            st.markdown(f"""
            <div class="tree" style="--i: {i}; font-size: {tree_size}rem;">
                {['🌱', '🌿', '🌲', '🌳'][i % 4]}
            </div>
            """, unsafe_allow_html=True)
        
        # If more than 15 trees, show a message
        if trees_planted > 15:
            st.markdown(f"""
            <div style="text-align: center; margin-top: 10px; color: #2E7D32;">
                <b>+{trees_planted - 15} more trees in your forest</b>
            </div>
            """, unsafe_allow_html=True)
        
        # Show CO2 absorbed by the forest
        co2_absorbed = trees_planted * 21  # 21kg per tree per year
        st.markdown(f"""
        <div style="text-align: center; margin-top: 15px;">
            <div style="font-size: 1.2rem; font-weight: 600; color: #2E7D32;">
                Your forest absorbs approximately {co2_absorbed}kg of CO₂ per year! 
            </div>
            <div style="font-size: 0.9rem; color: #558B2F; margin-top: 5px;">
                That's equivalent to driving approximately {co2_absorbed * 5.3:.0f}km in an average car.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close forest container
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close sustainability challenges container

def display_achievements_dashboard():
    """Display the environmental achievements dashboard"""
    if not st.session_state.achievements:
        return
    
    st.markdown("<div class='chart-container' style='border-left: 4px solid #FFC107;'>", unsafe_allow_html=True)
    st.markdown("<p class='stats-section-title'>🏆 Your Green Achievements</p>", unsafe_allow_html=True)
    
    # Define badge styling
    st.markdown("""
    <style>
    @keyframes badgeShine {
        0% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 215, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0); }
    }
    
    @keyframes badgeRotate {
        0% { transform: rotateY(0deg); }
        100% { transform: rotateY(360deg); }
    }
    
    .badges-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
        margin: 20px 0;
    }
    
    .badge-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F8F8 100%);
        border-radius: 15px;
        padding: 20px;
        width: 180px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        position: relative;
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    .badge-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 20px rgba(0, 0, 0, 0.1);
    }
    
    .badge-card:hover .badge-icon {
        animation: badgeRotate 1s ease-in-out;
    }
    
    .badge-card::before {
        content: "";
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #FFD700, #FFC107, #FFD700);
        z-index: -1;
        border-radius: 17px;
        opacity: 0.7;
        animation: badgeShine 2s infinite;
    }
    
    .badge-icon {
        font-size: 3rem;
        margin: 10px 0;
        display: inline-block;
    }
    
    .badge-title {
        color: #333;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 10px 0;
    }
    
    .badge-description {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }
    
    .badge-date {
        color: #999;
        font-size: 0.8rem;
        font-style: italic;
    }
    </style>
    
    <div class="badges-container">
    """, unsafe_allow_html=True)
    
    # Display each badge
    for achievement in st.session_state.achievements:
        st.markdown(f"""
        <div class="badge-card">
            <div class="badge-icon">{achievement['icon']}</div>
            <div class="badge-title">{achievement['title']}</div>
            <div class="badge-description">{achievement['description']}</div>
            <div class="badge-date">Earned on {achievement['date']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close badges container
    
    # Display impact summary
    st.markdown(f"""
    <div style='text-align: center; margin-top: 20px;'>
        <div style='font-weight: 600; color: #333; font-size: 1.2rem; margin-bottom: 15px;'>Your Environmental Impact</div>
        <div style='display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;'>
            <div style='background: linear-gradient(135deg, #F1F8E9 0%, #DCEDC8 100%); padding: 15px; border-radius: 10px; width: 180px;'>
                <div style='font-size: 2.5rem; color: #558B2F;'>{st.session_state.impact_milestones['trees_planted']}</div>
                <div style='color: #558B2F;'>Trees Planted</div>
            </div>
            <div style='background: linear-gradient(135deg, #E0F2F1 0%, #B2DFDB 100%); padding: 15px; border-radius: 10px; width: 180px;'>
                <div style='font-size: 2.5rem; color: #00695C;'>{st.session_state.impact_milestones['co2_offset']:.1f}kg</div>
                <div style='color: #00695C;'>CO₂ Offset</div>
            </div>
            <div style='background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); padding: 15px; border-radius: 10px; width: 180px;'>
                <div style='font-size: 2.5rem; color: #2E7D32;'>{st.session_state.impact_milestones['offset_actions']}</div>
                <div style='color: #2E7D32;'>Green Actions</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close chart container

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
        page = st.radio("", ["Add Journey", "View History", "Statistics", "Environmental Impact", "Eco-Challenges"], 
                    format_func=lambda x: {
                        "Add Journey": "➕ Add Journey",
                        "View History": "📖 View History",
                        "Statistics": "📊 Statistics",
                        "Environmental Impact": "🌍 Environmental Impact",
                        "Eco-Challenges": "🌱 Eco-Challenges"
                    }.get(x, x))
    
    # Load existing data
    df = load_data()
    
    # Display the selected page
    if page == "Add Journey":
        show_journey_form(df)
    elif page == "View History":
        show_journey_history(df)
    elif page == "Statistics":
        show_statistics(df)
    elif page == "Environmental Impact":
        display_achievements_dashboard()
    elif page == "Eco-Challenges":
        display_eco_challenges(df)

def display_carbon_offset_options(co2_emissions):
    """Display carbon offset options with interactive animations."""
    # Calculate offset options
    offset_options = utils.calculate_carbon_offset_options(co2_emissions)
    
    # No need to show if there are no emissions
    if co2_emissions <= 0:
        return
    
    # Add the CSS for carbon offset animations and styling
    st.markdown("""
    <style>
    @keyframes greenWave {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes growAndShrink {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes leafShimmer {
        0% { filter: hue-rotate(0deg) brightness(1); }
        50% { filter: hue-rotate(20deg) brightness(1.2); }
        100% { filter: hue-rotate(0deg) brightness(1); }
    }
    
    @keyframes carbonOffsetFadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulseGreen {
        0% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
        100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
    }
    
    @keyframes slowSpin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .carbon-offset-container {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 25px 0;
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.08);
        position: relative;
        overflow: hidden;
        animation: carbonOffsetFadeIn 0.7s ease-out;
    }
    
    .offset-header {
        text-align: center;
        margin-bottom: 20px;
        position: relative;
    }
    
    .offset-header h3 {
        color: #2e7d32;
        font-size: 1.6rem;
        font-weight: 600;
        margin-bottom: 5px;
        position: relative;
        display: inline-block;
    }
    
    .offset-header h3::after {
        content: '';
        position: absolute;
        bottom: -5px;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #4CAF50, transparent);
    }
    
    .leaves-decoration {
        position: absolute;
        top: -15px;
        right: -15px;
        font-size: 3rem;
        opacity: 0.2;
        transform-origin: center;
        animation: growAndShrink 4s ease-in-out infinite;
    }
    
    .offset-description {
        text-align: center;
        color: #37474f;
        margin-bottom: 20px;
        font-size: 1.1rem;
    }
    
    .offset-options-container {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 20px;
        margin: 20px 0;
    }
    
    .offset-option-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 20px;
        width: 280px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        animation: carbonOffsetFadeIn 0.7s ease-out forwards;
        opacity: 0;
    }
    
    .offset-option-card:nth-child(1) { animation-delay: 0.1s; }
    .offset-option-card:nth-child(2) { animation-delay: 0.2s; }
    .offset-option-card:nth-child(3) { animation-delay: 0.3s; }
    .offset-option-card:nth-child(4) { animation-delay: 0.4s; }
    
    .offset-option-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }
    
    .offset-option-icon {
        font-size: 2rem;
        margin-bottom: 10px;
        display: inline-block;
        animation: greenWave 3s ease-in-out infinite;
    }
    
    .offset-option-name {
        font-weight: 600;
        color: #2e7d32;
        font-size: 1.2rem;
        margin-bottom: 8px;
        position: relative;
    }
    
    .offset-option-name::after {
        content: '';
        position: absolute;
        bottom: -4px;
        left: 0;
        width: 40px;
        height: 2px;
        background-color: #4CAF50;
    }
    
    .offset-option-description {
        color: #546e7a;
        margin-bottom: 15px;
        font-size: 0.95rem;
    }
    
    .offset-option-impact {
        background-color: #e8f5e9;
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 15px;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
    }
    
    .offset-option-impact::before {
        content: "🌱";
        margin-right: 8px;
        animation: leafShimmer 2s infinite;
    }
    
    .offset-option-cost {
        font-weight: 600;
        color: #2e7d32;
        font-size: 1.2rem;
        margin-top: auto;
    }
    
    .offset-option-button {
        background: linear-gradient(90deg, #4CAF50, #81C784);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 10px 20px;
        font-weight: 500;
        margin-top: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        animation: pulseGreen 2s infinite;
    }
    
    .offset-option-button:hover {
        background: linear-gradient(90deg, #388E3C, #66BB6A);
        transform: scale(1.05);
    }
    
    .offset-progress-container {
        text-align: center;
        margin-top: 20px;
        padding: 15px;
        background: rgba(255, 255, 255, 0.7);
        border-radius: 10px;
    }
    
    .offset-progress-icon {
        font-size: 1.5rem;
        margin-right: 10px;
        display: inline-block;
        animation: greenWave 2s ease-in-out infinite;
    }
    
    .offset-background-decoration {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        z-index: -1;
        opacity: 0.05;
        pointer-events: none;
    }
    
    .spinning-earth {
        position: absolute;
        top: -50px;
        right: -50px;
        font-size: 6rem;
        opacity: 0.1;
        animation: slowSpin 20s linear infinite;
    }
    
    .offset-footer {
        text-align: center;
        font-size: 0.9rem;
        color: #558b2f;
        margin-top: 15px;
        font-style: italic;
    }
    
    /* Tree animation elements */
    .tree-animation-container {
        height: 50px;
        margin-top: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .tree {
        font-size: 1.8rem;
        margin: 0 5px;
        animation: greenWave 2s ease-in-out infinite;
    }
    
    .tree:nth-child(1) { animation-delay: 0s; }
    .tree:nth-child(2) { animation-delay: 0.5s; }
    .tree:nth-child(3) { animation-delay: 1s; }
    .tree:nth-child(4) { animation-delay: 1.5s; }
    .tree:nth-child(5) { animation-delay: 2s; }
    </style>
    """, unsafe_allow_html=True)
    
    # Begin the container
    st.markdown('<div class="carbon-offset-container">', unsafe_allow_html=True)
    
    # Add a spinning earth in the background
    st.markdown('<div class="spinning-earth">🌍</div>', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="offset-header">
        <span class="leaves-decoration">🍃</span>
        <h3>🌱 Carbon Offset Opportunities 🌱</h3>
        <p class="offset-description">Make a positive environmental impact with just one click!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display tree animation
    st.markdown('<div class="tree-animation-container">', unsafe_allow_html=True)
    
    # Only show up to 5 trees, regardless of how many are needed for offset
    tree_count = min(5, offset_options['trees'])
    for i in range(tree_count):
        st.markdown(f'<div class="tree">🌳</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close tree animation container
    
    # Options container
    st.markdown('<div class="offset-options-container">', unsafe_allow_html=True)
    
    # Display each offset option as a card
    for option in offset_options['suggestions']:
        option_id = option['name'].lower().replace(' ', '_')
        
        st.markdown(f"""
        <div class="offset-option-card">
            <div class="offset-option-icon">{option['icon']}</div>
            <div class="offset-option-name">{option['name']}</div>
            <div class="offset-option-description">{option['description']}</div>
            <div class="offset-option-impact">{option['impact']}</div>
            <div class="offset-option-cost">${option['cost']:.2f}</div>
            <button class="offset-option-button" onclick="alert('Thank you for your interest in offsetting your carbon footprint!')">
                Offset Now
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    # Add a footer
    st.markdown("""
    <div class="offset-footer">
        Carbon offset calculations are estimates. For actual offsetting, we'd connect to verified carbon offset providers.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close options container
    st.markdown('</div>', unsafe_allow_html=True)  # Close main container
    
    # Also add a regular Streamlit button for actual functionality (since the HTML button doesn't work with Streamlit)
    st.markdown("### Offset Your Carbon Footprint")
    
    # Create a row of buttons for each offset option
    cols = st.columns(len(offset_options['suggestions']))
    
    for i, option in enumerate(offset_options['suggestions']):
        with cols[i]:
            if st.button(f"Offset with {option['name']} (${option['cost']:.2f})", key=f"offset_btn_{i}"):
                # Save offset in session state
                st.session_state.offset_selected = option['name']
                st.session_state.offset_amount = option['cost']
                
                # Add to offset history
                import datetime
                offset_record = {
                    'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                    'option': option['name'],
                    'amount': option['cost'],
                    'co2_kg': co2_emissions,
                    'icon': option['icon']
                }
                st.session_state.carbon_offsets.append(offset_record)
                
                # Update total offset
                st.session_state.total_offset += option['cost']
                
                # Show success message with confirmation animation
                st.success(f"Thank you for offsetting your carbon footprint with {option['name']}! This would cost ${option['cost']:.2f} with a real provider.")
                
                # Show confetti animation
                st.balloons()
                
                # Update impact milestones
                update_impact_milestones(option, co2_emissions)
                
                # Check if we should display achievement
                check_achievements()

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
        
        .offset-button {
            display: inline-block;
            background: linear-gradient(90deg, #4CAF50, #66BB6A);
            color: white;
            font-weight: 500;
            border-radius: 30px;
            padding: 10px 20px;
            margin-top: 15px;
            text-align: center;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            animation: fadeIn 1.5s ease-out;
        }
        
        .offset-button:hover {
            background: linear-gradient(90deg, #388E3C, #4CAF50);
            transform: translateY(-3px);
            box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
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
        co2 = 0
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
        
        # Add a footer with carbon offset link if CO2 emissions exist
        if co2 > 0:
            st.markdown(f"""
            <div class="journey-footer">
                Track more journeys to improve your insights and eco-driving score!
                <br><br>
                <div style="position: relative; display: inline-block;">
                    <div style="position: absolute; top: -15px; right: -15px; font-size: 1.2rem; animation: float 3s ease-in-out infinite;">🌿</div>
                    <div style="position: absolute; top: -12px; left: -15px; font-size: 1.2rem; animation: float 2.5s ease-in-out infinite;">🌱</div>
                    <a class="offset-button" href="#" onclick="setTimeout(function() {{ document.getElementById('carbon-offset-section').scrollIntoView(); }}, 100); return false;">
                        <span style="display: inline-block; margin-right: 8px; animation: float 2s ease-in-out infinite;">🌳</span>
                        Offset Your Carbon Footprint ({co2:.1f} kg CO₂)
                        <span style="display: inline-block; margin-left: 8px; animation: float 2s ease-in-out infinite 0.5s;">🌍</span>
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="journey-footer">Track more journeys to improve your insights and eco-driving score!</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close insight-section
        st.markdown('</div>', unsafe_allow_html=True)  # Close journey-card
    
    # Add a separator
    st.markdown("<hr style='margin: 30px 0; border: 0; height: 1px; background: linear-gradient(to right, transparent, #4361EE, transparent);'>", unsafe_allow_html=True)
    
    # Carbon offset section (if emissions exist)
    if co2 > 0:
        st.markdown('<div id="carbon-offset-section"></div>', unsafe_allow_html=True)  # Anchor for scrolling
        
        # Add carbon offset options with more prominent styling
        st.markdown("""
        <style>
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
            100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
        }
        .eco-button-container {
            text-align: center;
            margin: 15px 0;
            position: relative;
        }
        .eco-button-container::before {
            content: '🌿';
            position: absolute;
            font-size: 1.5rem;
            top: -10px;
            left: 25%;
            animation: float 3s ease-in-out infinite;
        }
        .eco-button-container::after {
            content: '🌱';
            position: absolute;
            font-size: 1.5rem;
            top: -5px;
            right: 25%;
            animation: float 2.5s ease-in-out infinite;
        }
        </style>
        <div class="eco-button-container">
            <div style="font-size: 1.2rem; margin-bottom: 5px; color: #2e7d32; font-weight: 500;">
                Make a difference today!
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Use columns to center the button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💚 View Carbon Offset Options 💚", key="view_offset_options", 
                      use_container_width=True,
                      help="See how you can offset the carbon footprint of this journey"):
                st.balloons()  # Show balloons for added fun
                display_carbon_offset_options(co2)

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
                    max_value=datetime.datetime.now().date()
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
        
        # Add carbon offset button with playful animations
        st.markdown("""
        <style>
        @keyframes growing {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        @keyframes leafWave {
            0% { transform: rotate(-5deg); }
            50% { transform: rotate(5deg); }
            100% { transform: rotate(-5deg); }
        }
        
        .eco-card {
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
            animation: growing 4s infinite ease-in-out;
        }
        
        .eco-card-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #2e7d32;
            margin-bottom: 15px;
            position: relative;
            display: inline-block;
        }
        
        .eco-card-title::before, .eco-card-title::after {
            content: "🌿";
            position: absolute;
            top: 0;
            font-size: 1.2rem;
            animation: leafWave 3s infinite ease-in-out;
        }
        
        .eco-card-title::before {
            left: -30px;
            animation-delay: 0.5s;
        }
        
        .eco-card-title::after {
            right: -30px;
        }
        
        .eco-card-description {
            color: #37474f;
            margin-bottom: 15px;
            font-size: 1rem;
        }
        
        .eco-background {
            position: absolute;
            font-size: 8rem;
            opacity: 0.05;
            bottom: -30px;
            right: -20px;
            transform: rotate(-15deg);
        }
        </style>
        
        <div class="eco-card">
            <div class="eco-background">🌍</div>
            <div class="eco-card-title">Make a Green Impact</div>
            <div class="eco-card-description">
                Offset your carbon footprint of {stats['co2_emissions']:.1f} kg CO₂ with just one click!
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a more visually appealing button with columns
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💚 View Carbon Offset Options 💚", key="stats_offset_button", 
                       use_container_width=True, 
                       help="Explore ways to offset your carbon footprint from all journeys"):
                st.balloons()  # Add balloons for fun
                display_carbon_offset_options(stats['co2_emissions'])
        
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
    
    # Add carbon offset history section if there are any offsets
    if st.session_state.carbon_offsets:
        st.markdown("<div class='chart-container' style='border-left: 4px solid #4CAF50;'>", unsafe_allow_html=True)
        st.markdown("<p class='stats-section-title'>🌿 Your Carbon Offset History</p>", unsafe_allow_html=True)
        
        # Display total offset amount
        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background-color: #e8f5e9; border-radius: 10px; margin-bottom: 20px;'>
            <div style='font-size: 1.2rem; color: #2e7d32; margin-bottom: 5px;'>Total Carbon Offset Contribution</div>
            <div style='font-size: 2.5rem; font-weight: bold; color: #2e7d32;'>${st.session_state.total_offset:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display offset history in a table with animations
        st.markdown("""
        <style>
        .offset-history-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        }
        
        .offset-history-table th {
            background-color: #e8f5e9;
            color: #2e7d32;
            font-weight: 600;
            text-align: left;
            padding: 12px 15px;
        }
        
        .offset-history-table td {
            padding: 10px 15px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .offset-history-table tr {
            background-color: white;
            transition: all 0.3s ease;
        }
        
        .offset-history-table tr:hover {
            background-color: #f9fff9;
            transform: translateX(5px);
        }
        
        .offset-history-table tr:nth-child(even) {
            background-color: #fbfbfb;
        }
        
        .offset-history-icon {
            font-size: 1.5rem;
            margin-right: 5px;
            animation: float 3s ease-in-out infinite;
            display: inline-block;
        }
        
        .offset-amount {
            font-weight: 600;
            color: #2e7d32;
        }
        
        .offset-co2 {
            color: #555;
            font-style: italic;
        }
        </style>
        
        <table class="offset-history-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Method</th>
                    <th>CO₂ Offset</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
        """, unsafe_allow_html=True)
        
        # Add each offset record to the table
        for offset in st.session_state.carbon_offsets:
            st.markdown(f"""
            <tr>
                <td>{offset['date']}</td>
                <td><span class="offset-history-icon">{offset['icon']}</span> {offset['option']}</td>
                <td class="offset-co2">{offset['co2_kg']:.1f} kg</td>
                <td class="offset-amount">${offset['amount']:.2f}</td>
            </tr>
            """, unsafe_allow_html=True)
            
        st.markdown("""
            </tbody>
        </table>
        """, unsafe_allow_html=True)
        
        # Add a fun encouragement message
        co2_total = sum(offset['co2_kg'] for offset in st.session_state.carbon_offsets)
        trees_planted = sum(1 for offset in st.session_state.carbon_offsets if 'Tree' in offset['option'])
        
        st.markdown(f"""
        <div style='background-color: #e8f5e9; padding: 15px; border-radius: 10px; margin-top: 15px; text-align: center;'>
            <div style='font-weight: 600; color: #2e7d32; margin-bottom: 10px;'>Your Impact</div>
            <div style='display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;'>
                <div style='background-color: white; padding: 10px 20px; border-radius: 8px; min-width: 150px;'>
                    <div style='font-size: 2rem;'>🌍</div>
                    <div style='font-weight: 600;'>{co2_total:.1f} kg</div>
                    <div style='font-size: 0.9rem; color: #555;'>CO₂ Offset</div>
                </div>
                <div style='background-color: white; padding: 10px 20px; border-radius: 8px; min-width: 150px;'>
                    <div style='font-size: 2rem;'>🌳</div>
                    <div style='font-weight: 600;'>{trees_planted}</div>
                    <div style='font-size: 0.9rem; color: #555;'>Trees Planted</div>
                </div>
                <div style='background-color: white; padding: 10px 20px; border-radius: 8px; min-width: 150px;'>
                    <div style='font-size: 2rem;'>💚</div>
                    <div style='font-weight: 600;'>{len(st.session_state.carbon_offsets)}</div>
                    <div style='font-size: 0.9rem; color: #555;'>Offset Actions</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close chart container
    
    # Display the achievements dashboard if there are any achievements
    if st.session_state.achievements:
        display_achievements_dashboard()
    
    # Display sustainability challenges section
    display_sustainability_challenges(stats)
    
    # Display route optimization suggestions
    display_route_optimization(stats)
    
    # Display driving pattern analysis
    display_driving_patterns_analysis(stats)
    
    # Add a tip or insight at the bottom
    if stats['total_journeys'] > 1:
        st.markdown("""
        <div style="background-color: #f1f8ff; padding: 15px; border-radius: 10px; margin-top: 20px; 
                    border-left: 3px solid #4CC9F0; font-style: italic; text-align: center;">
            <b>✨ Insight:</b> Keep logging your journeys to see more detailed statistics and trends over time!
        </div>
        """, unsafe_allow_html=True)
    
    # Check for any new achievements to display
    check_achievements()

# Display the eco-challenges weekly missions
def display_eco_challenges(df):
    """Display gamified eco-challenges and weekly missions"""
    st.markdown("<h2>🌍 Weekly Eco-Challenges</h2>", unsafe_allow_html=True)
    
    # Check if we need to initialize challenges
    if 'weekly_challenges' not in st.session_state:
        stats = calculate_statistics(df)
        st.session_state.weekly_challenges = generate_weekly_eco_challenges(stats)
        st.session_state.total_eco_points = 0
        st.session_state.completed_challenges = []
    
    # Update progress on all active challenges
    if len(df) > 0:
        st.session_state.weekly_challenges = update_eco_challenge_progress(
            st.session_state.weekly_challenges, 
            df
        )
    
    # Check for newly completed challenges
    for challenge in st.session_state.weekly_challenges:
        if challenge.get('completed', False) and challenge['id'] not in st.session_state.completed_challenges:
            # Add points
            st.session_state.total_eco_points += challenge.get('points', 0)
            # Mark as counted
            st.session_state.completed_challenges.append(challenge['id'])
            # Set up celebration
            st.session_state.show_achievement = True
            st.session_state.achievement_title = f"Challenge Completed: {challenge['title']}"
            st.session_state.achievement_description = f"You've earned {challenge['points']} eco-points!"
            st.session_state.achievement_icon = challenge.get('icon', '🏆')
    
    # Display the eco points
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                    padding: 15px; border-radius: 15px; text-align: center; 
                    color: white; margin-bottom: 20px;">
            <div style="font-size: 1.3rem; font-weight: 600; margin-bottom: 5px;">🏆 Your Eco-Points</div>
            <div style="font-size: 2.5rem; font-weight: 700;">{st.session_state.total_eco_points}</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">Complete weekly challenges to earn more!</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Display the leaderboard
    display_leaderboard(st.session_state.total_eco_points)
    
    # Style definitions for challenge cards
    st.markdown(
        """
        <style>
        @keyframes glowPulse {
            0% { box-shadow: 0 0 10px rgba(40, 167, 69, 0.5); }
            50% { box-shadow: 0 0 20px rgba(40, 167, 69, 0.8); }
            100% { box-shadow: 0 0 10px rgba(40, 167, 69, 0.5); }
        }
        
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        
        .eco-challenges-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .challenge-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .challenge-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        }
        
        .challenge-card.completed {
            background: linear-gradient(135deg, #e9f9f0 0%, #d4f7e6 100%);
            animation: glowPulse 2s infinite;
        }
        
        .challenge-card.completed::after {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, 
                rgba(255,255,255, 0) 0%, 
                rgba(255,255,255, 0.4) 50%, 
                rgba(255,255,255, 0) 100%);
            background-size: 200% 100%;
            animation: shimmer 3s infinite;
            pointer-events: none;
        }
        
        .challenge-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .challenge-icon {
            font-size: 2.5rem;
            color: #28a745;
        }
        
        .challenge-header-text {
            flex: 1;
        }
        
        .challenge-title {
            font-weight: 600;
            font-size: 1.2rem;
            color: #212529;
            margin-bottom: 5px;
        }
        
        .challenge-meta {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .challenge-points {
            background-color: #e9f9f0;
            color: #28a745;
            font-weight: 600;
            font-size: 0.9rem;
            padding: 3px 8px;
            border-radius: 20px;
        }
        
        .challenge-difficulty {
            font-size: 0.8rem;
            color: #6c757d;
        }
        
        .difficulty-easy {
            color: #20c997;
        }
        
        .difficulty-medium {
            color: #fd7e14;
        }
        
        .difficulty-hard {
            color: #dc3545;
        }
        
        .challenge-description {
            font-size: 1rem;
            color: #495057;
            margin-bottom: 20px;
            line-height: 1.5;
        }
        
        .progress-container {
            background-color: #e9ecef;
            height: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            border-radius: 5px;
            width: var(--progress-width);
            transition: width 1s ease;
        }
        
        .progress-text {
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            color: #6c757d;
        }
        
        .challenge-status {
            margin-top: 15px;
            font-size: 0.9rem;
        }
        
        .status-completed {
            color: #28a745;
            font-weight: 600;
        }
        
        .challenge-completed-badge {
            position: absolute;
            top: -10px;
            right: -10px;
            background: #28a745;
            color: white;
            font-weight: 600;
            font-size: 0.8rem;
            padding: 5px 10px;
            border-radius: 20px;
            transform: rotate(15deg);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        .challenge-tip {
            margin-top: 15px;
            background-color: #e9f9f0;
            padding: 10px 15px;
            border-radius: 10px;
            font-size: 0.9rem;
            color: #28a745;
            border-left: 3px solid #28a745;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # Display challenge cards
    st.markdown('<div class="eco-challenges-container">', unsafe_allow_html=True)
    
    for challenge in st.session_state.weekly_challenges:
        # Get challenge details
        challenge_id = challenge.get('id', '')
        title = challenge.get('title', 'Challenge')
        description = challenge.get('description', '')
        icon = challenge.get('icon', '🌱')
        points = challenge.get('points', 0)
        difficulty = challenge.get('difficulty', 'medium')
        progress = challenge.get('progress', 0)
        completed = challenge.get('completed', False)
        tip = challenge.get('tips', '')
        
        # Difficulty display
        difficulty_display = {
            'easy': '⭐ Easy',
            'medium': '⭐⭐ Medium',
            'hard': '⭐⭐⭐ Hard'
        }.get(difficulty, difficulty.capitalize())
        
        # Challenge card HTML
        card_class = "challenge-card completed" if completed else "challenge-card"
        
        current_value_display = ""
        if 'current_value' in challenge:
            unit = challenge.get('unit', '')
            value = challenge['current_value']
            
            # Format based on unit type
            if unit == 'km/L':
                current_value_display = f"Current: {value} km/L"
            elif unit == 'reduction_factor':
                current_value_display = f"Current reduction: {value}%"
            elif unit == 'kg_co2':
                current_value_display = f"Best day: {value} kg CO₂"
            elif unit == 'variation':
                current_value_display = f"Current variation: {value}%"
            elif unit == 'streak':
                current_value_display = f"Current streak: {value} journeys"
            elif unit == 'days':
                current_value_display = f"Current streak: {value} days"
            elif unit == 'purposes':
                current_value_display = f"Max purposes: {value}"
            elif unit == 'percentage':
                current_value_display = f"Current: {value}%"
            else:
                current_value_display = f"Current: {value}"
        
        # Create card HTML
        st.markdown(
            f"""
            <div class="{card_class}" id="challenge-{challenge_id}">
                {f'<div class="challenge-completed-badge">COMPLETED!</div>' if completed else ''}
                <div class="challenge-header">
                    <div class="challenge-icon">{icon}</div>
                    <div class="challenge-header-text">
                        <div class="challenge-title">{title}</div>
                        <div class="challenge-meta">
                            <div class="challenge-points">{points} points</div>
                            <div class="challenge-difficulty difficulty-{difficulty}">{difficulty_display}</div>
                        </div>
                    </div>
                </div>
                
                <div class="challenge-description">{description}</div>
                
                <div class="progress-container">
                    <div class="progress-bar" style="--progress-width: {progress}%;"></div>
                </div>
                
                <div class="progress-text">
                    <span>{progress}% complete</span>
                    <span>{current_value_display}</span>
                </div>
                
                {f'<div class="challenge-status status-completed">✅ Challenge completed! +{points} points</div>' if completed else ''}
                
                <div class="challenge-tip">
                    <strong>Tip:</strong> {tip}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Button to reset challenges (for testing)
    if st.button("Generate New Challenges"):
        stats = calculate_statistics(df)
        st.session_state.weekly_challenges = generate_weekly_eco_challenges(stats)

if __name__ == "__main__":
    main()
