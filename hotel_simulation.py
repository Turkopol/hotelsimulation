import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Sayfa yapılandırması
st.set_page_config(
    page_title="Hotel Management Simulation",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #4F46E5;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        background-color: #4F46E5;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #4338CA;
    }
</style>
""", unsafe_allow_html=True)

# Session state başlatma
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
    st.session_state.current_round = 0
    st.session_state.season = 'Summer'
    st.session_state.team_name = ''
    
    # Game State
    st.session_state.game_state = {
        'cash': 500000,
        'rooms': 20,
        'room_condition': 85,
        'permanent_staff': 15,
        'temporary_staff': 5,
        'staff_competence': 70,
        'staff_salary': 2500,
        'long_term_loan': 200000,
        'total_revenue': 0,
        'total_costs': 0,
        'net_profit': 0,
        'occupancy_rate': 0,
        'customer_satisfaction': 75,
        'employee_satisfaction': 70,
        'market_share': 12.5,
        'share_price': 10.0,
        'history': []
    }
    
    # Decisions
    st.session_state.decisions = {
        'walk_in_rate': 120,
        'advance_1_rooms': 1000,
        'advance_2_rooms': 800,
        'permanent_staff_change': 0,
        'temporary_staff': 5,
        'staff_salary': 2500,
        'training_budget': 5000,
        'new_room_batches': 0,
        'renovation_budget': 0,
        'maintenance_budget': 8000,
        'marketing_budget': 10000,
        'cost_saving_operations': 0,
        'cost_saving_admin': 0,
        'loan_change': 0,
        'credit_term': 30,
        'dividend_payout': 0
    }

# Rakip takımlar
competitors = [
    {'name': 'Team 1', 'market_share': 12.5, 'satisfaction': 75},
    {'name': 'Team 2', 'market_share': 14.2, 'satisfaction': 78},
    {'name': 'Team 3', 'market_share': 11.8, 'satisfaction': 72},
    {'name': 'Team 4', 'market_share': 13.1, 'satisfaction': 76},
]

def calculate_results():
    """Tur sonuçlarını hesapla"""
    state = st.session_state.game_state
    dec = st.session_state.decisions
    
    # Kapasite hesaplamaları
    total_capacity = state['rooms'] * 180
    advance_sales = (dec['advance_1_rooms'] + dec['advance_2_rooms']) * 0.4
    walk_in_sales = total_capacity * 0.5 * (1 - dec['walk_in_rate'] / 200)
    total_nights_sold = min(advance_sales + walk_in_sales, total_capacity)
    
    # Gelir hesaplamaları
    avg_advance_rate = dec['walk_in_rate'] * 0.8 * (1 - dec['advance_1_rooms'] / 5000)
    total_revenue = (advance_sales * avg_advance_rate) + (walk_in_sales * dec['walk_in_rate'])
    
    # Maliyet hesaplamaları
    staff_cost = (state['permanent_staff'] * dec['staff_salary'] + dec['temporary_staff'] * 1800) * 6
    operating_cost = total_nights_sold * 25 * (1 - dec['cost_saving_operations'] / 100)
    admin_cost = 30000 * (1 - dec['cost_saving_admin'] / 100)
    total_costs = (staff_cost + operating_cost + admin_cost + 
                   dec['marketing_budget'] + dec['maintenance_budget'] + 
                   dec['training_budget'] + (state['long_term_loan'] * 0.03))
    
    net_profit = total_revenue - total_costs
    occupancy_rate = (total_nights_sold / total_capacity) * 100
    
    # Memnuniyet skorları
    satisfaction_score = min(100, max(40, 
        60 + (state['room_condition'] - 70) * 0.3 + 
        (state['staff_competence'] - 60) * 0.2 + 
        (dec['marketing_budget'] / 500) * 0.1 - 
        (dec['walk_in_rate'] - 100) * 0.15
    ))
    
    employee_satisfaction = min(100, max(40,
        60 + (dec['staff_salary'] - 2000) / 50 + 
        (dec['training_budget'] / 500) - 
        (total_nights_sold / (state['permanent_staff'] + dec['temporary_staff']) - 100) / 10
    ))
    
    # Pazar payı
    competitiveness = (satisfaction_score + employee_satisfaction) / 2
    market_share = max(8, min(20, 
        state['market_share'] * 0.7 + (competitiveness / 10) * 0.3
    ))
    
    # Hisse fiyatı
    eps = net_profit / 100000
    share_price = max(5, state['share_price'] * 0.8 + eps * 15)
    
    # Oda durumu
    new_condition = max(40, 
        state['room_condition'] - 5 + 
        (dec['maintenance_budget'] / 1000) + 
        (dec['renovation_budget'] / state['rooms'] / 1000)
    )
    
    # Personel yetkinliği
    new_competence = min(100, 
        state['staff_competence'] * 0.95 + (dec['training_budget'] / 1000)
    )
    
    # Yatırımlar
    investments = dec['new_room_batches'] * 150000 + dec['renovation_budget']
    new_cash = state['cash'] + net_profit - investments - dec['dividend_payout'] + dec['loan_change']
    
    # State güncelleme
    st.session_state.game_state.update({
        'cash': new_cash,
        'rooms': state['rooms'] + (dec['new_room_batches'] * 5),
        'room_condition': new_condition,
        'permanent_staff': state['permanent_staff'] + dec['permanent_staff_change'],
        'temporary_staff': dec['temporary_staff'],
        'staff_competence': new_competence,
        'staff_salary': dec['staff_salary'],
        'total_revenue': total_revenue,
        'total_costs': total_costs,
        'net_profit': net_profit,
        'occupancy_rate': occupancy_rate,
        'customer_satisfaction': satisfaction_score,
        'employee_satisfaction': employee_satisfaction,
        'market_share': market_share,
        'share_price': share_price,
        'long_term_loan': state['long_term_loan'] + dec['loan_change']
    })
    
    # Geçmişe ekle
    st.session_state.game_state['history'].append({
        'round': st.session_state.current_round,
        'season': st.session_state.season,
        'revenue': total_revenue,
        'profit': net_profit,
        'occupancy': occupancy_rate,
        'satisfaction': satisfaction_score,
        'market_share': market_share,
        'share_price': share_price
    })
    
    # Sezon değiştir
    if st.session_state.season == 'Summer':
        st.session_state.season = 'Winter'
    else:
        st.session_state.season = 'Summer'
        st.session_state.current_round += 1

def show_welcome_page():
    """Karşılama sayfası"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 class='main-header'>🏨 Hotel Management Simulation</h1>", unsafe_allow_html=True)
        st.markdown("### Manage your hotel business and compete for market leadership")
        
        st.markdown("---")
        
        team_name = st.text_input("Enter Your Team Name", placeholder="Team Alpha")
        
        st.markdown("---")
        
        st.markdown("#### 🎯 Learning Objectives:")
        st.markdown("""
        - **Pricing & Revenue Management** - Optimize room rates and advance sales
        - **Human Resources Management** - Balance permanent and temporary staff
        - **Capacity & Quality Management** - Invest in facilities and maintain quality
        - **Financial Decision Making** - Manage cash flow, loans, and dividends
        """)
        
        st.markdown("---")
        
        if st.button("🚀 Start Simulation", use_container_width=True):
            if team_name.strip():
                st.session_state.team_name = team_name
                st.session_state.game_started = True
                st.rerun()
            else:
                st.error("Please enter a team name!")

def show_dashboard():
    """Dashboard sayfası"""
    state = st.session_state.game_state
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"## 🏨 {st.session_state.team_name}")
        st.markdown(f"**Round {st.session_state.current_round}** - {st.session_state.season} Season")
    
    with col2:
        st.metric("💰 Cash", f"${state['cash']/1000:.0f}k")
    
    with col3:
        st.metric("📈 Share Price", f"${state['share_price']:.2f}")
    
    st.markdown("---")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏨 Occupancy Rate", f"{state['occupancy_rate']:.1f}%")
    
    with col2:
        st.metric("😊 Customer Satisfaction", f"{state['customer_satisfaction']:.0f}%")
    
    with col3:
        st.metric("💵 Net Profit", f"${state['net_profit']/1000:.0f}k")
    
    with col4:
        st.metric("🛏️ Total Rooms", state['rooms'])
    
    st.markdown("---")
    
    # Charts
    if len(state['history']) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue & Profit Trend
            df_history = pd.DataFrame(state['history'])
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=df_history['round'], y=df_history['revenue'], 
                                     name='Revenue', line=dict(color='#667eea')))
            fig1.add_trace(go.Scatter(x=df_history['round'], y=df_history['profit'], 
                                     name='Profit', line=dict(color='#764ba2')))
            fig1.update_layout(title='Revenue & Profit Trend', height=300)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Market Share Trend
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=df_history['round'], y=df_history['market_share'], 
                                     fill='tozeroy', line=dict(color='#f093fb')))
            fig2.update_layout(title='Market Share Trend', height=300)
            st.plotly_chart(fig2, use_container_width=True)
    
    # Current Status
    st.markdown("### 📊 Current Operations Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏢 Facilities")
        st.write(f"**Total Rooms:** {state['rooms']}")
        st.write(f"**Condition:** {state['room_condition']:.0f}%")
        st.write(f"**Capacity/Season:** {state['rooms'] * 180} nights")
    
    with col2:
        st.markdown("#### 👥 Personnel")
        st.write(f"**Permanent Staff:** {state['permanent_staff']}")
        st.write(f"**Temporary Staff:** {state['temporary_staff']}")
        st.write(f"**Competence:** {state['staff_competence']:.0f}%")
    
    with col3:
        st.markdown("#### 💰 Financial")
        st.write(f"**Cash:** ${state['cash']/1000:.0f}k")
        st.write(f"**Long-term Loan:** ${state['long_term_loan']/1000:.0f}k")
        st.write(f"**Market Share:** {state['market_share']:.1f}%")

def show_decisions():
    """Karar sayfası"""
    st.markdown("## ⚙️ Make Your Decisions")
    st.markdown(f"**Round {st.session_state.current_round}** - {st.session_state.season} Season")
    st.markdown("---")
    
    dec = st.session_state.decisions
    
    # Sales & Pricing
    st.markdown("### 💵 Sales & Pricing")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dec['walk_in_rate'] = st.number_input(
            "Walk-in Rate ($)",
            min_value=50,
            max_value=300,
            value=dec['walk_in_rate'],
            help="Price per night for walk-in customers"
        )
    
    with col2:
        dec['advance_1_rooms'] = st.number_input(
            "Advance Sales (+1 period)",
            min_value=0,
            max_value=5000,
            value=dec['advance_1_rooms'],
            help="Rooms to sell for next period"
        )
    
    with col3:
        dec['advance_2_rooms'] = st.number_input(
            "Advance Sales (+2 periods)",
            min_value=0,
            max_value=5000,
            value=dec['advance_2_rooms'],
            help="Rooms to sell for period +2"
        )
    
    st.markdown("---")
    
    # Personnel Management
    st.markdown("### 👥 Personnel Management")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        dec['permanent_staff_change'] = st.number_input(
            "Permanent Staff Change",
            min_value=-10,
            max_value=10,
            value=dec['permanent_staff_change'],
            help="+/- staff count"
        )
    
    with col2:
        dec['temporary_staff'] = st.number_input(
            "Temporary Staff",
            min_value=0,
            max_value=50,
            value=dec['temporary_staff'],
            help="Number of temporary employees"
        )
    
    with col3:
        dec['staff_salary'] = st.number_input(
            "Staff Salary ($)",
            min_value=1500,
            max_value=5000,
            value=dec['staff_salary'],
            help="Monthly salary per permanent employee"
        )
    
    with col4:
        dec['training_budget'] = st.number_input(
            "Training Budget ($)",
            min_value=0,
            max_value=20000,
            value=dec['training_budget'],
            help="Budget for staff training"
        )
    
    st.markdown("---")
    
    # Facilities & Investments
    st.markdown("### 🏗️ Facilities & Investments")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dec['new_room_batches'] = st.number_input(
            "New Room Batches",
            min_value=0,
            max_value=10,
            value=dec['new_room_batches'],
            help="5 rooms per batch ($150k each)"
        )
    
    with col2:
        dec['renovation_budget'] = st.number_input(
            "Renovation Budget ($)",
            min_value=0,
            max_value=100000,
            value=dec['renovation_budget'],
            help="Improve room condition"
        )
    
    with col3:
        dec['maintenance_budget'] = st.number_input(
            "Maintenance Budget ($)",
            min_value=0,
            max_value=50000,
            value=dec['maintenance_budget'],
            help="Prevent deterioration"
        )
    
    st.markdown("---")
    
    # Marketing & Operations
    st.markdown("### 📢 Marketing & Operations")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dec['marketing_budget'] = st.number_input(
            "Marketing Budget ($)",
            min_value=0,
            max_value=50000,
            value=dec['marketing_budget'],
            help="Marketing communications"
        )
    
    with col2:
        dec['cost_saving_operations'] = st.number_input(
            "Cost Saving - Operations (%)",
            min_value=0,
            max_value=30,
            value=dec['cost_saving_operations'],
            help="Reduce operating costs (0-30%)"
        )
    
    with col3:
        dec['cost_saving_admin'] = st.number_input(
            "Cost Saving - Admin (%)",
            min_value=0,
            max_value=30,
            value=dec['cost_saving_admin'],
            help="Reduce admin costs (0-30%)"
        )
    
    st.markdown("---")
    
    # Financial Decisions
    st.markdown("### 💰 Financial Decisions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dec['loan_change'] = st.number_input(
            "Loan Change ($)",
            min_value=-200000,
            max_value=200000,
            value=dec['loan_change'],
            step=10000,
            help="Increase (+) or decrease (-) loan"
        )
    
    with col2:
        dec['credit_term'] = st.number_input(
            "Credit Term (days)",
            min_value=0,
            max_value=90,
            value=dec['credit_term'],
            help="Payment terms for advance sales"
        )
    
    with col3:
        dec['dividend_payout'] = st.number_input(
            "Dividend Payout ($)",
            min_value=0,
            max_value=100000,
            value=dec['dividend_payout'],
            help="Dividends to shareholders"
        )
    
    st.markdown("---")
    
    # Process Round Button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎯 Process Round", use_container_width=True, type="primary"):
            calculate_results()
            st.success("✅ Round processed successfully!")
            st.balloons()
            st.rerun()

def show_results():
    """Sonuçlar sayfası"""
    state = st.session_state.game_state
    
    st.markdown(f"## 📊 Round {st.session_state.current_round} Results")
    st.markdown(f"**{st.session_state.season} Season Performance**")
    st.markdown("---")
    
    # Financial Performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Financial Performance")
        st.metric("Total Revenue", f"${state['total_revenue']/1000:.0f}k")
        st.metric("Total Costs", f"${state['total_costs']/1000:.0f}k")
        st.metric("Net Profit", f"${state['net_profit']/1000:.0f}k", 
                 delta=f"{state['net_profit']/1000:.0f}k")
        st.metric("Share Price", f"${state['share_price']:.2f}")
    
    with col2:
        st.markdown("### 📈 Operational Performance")
        st.metric("Occupancy Rate", f"{state['occupancy_rate']:.1f}%")
        st.metric("Customer Satisfaction", f"{state['customer_satisfaction']:.0f}%")
        st.metric("Employee Satisfaction", f"{state['employee_satisfaction']:.0f}%")
        st.metric("Market Share", f"{state['market_share']:.1f}%")
    
    st.markdown("---")
    
    # Performance Charts
    if len(state['history']) > 1:
        st.markdown("### 📊 Historical Performance")
        
        df = pd.DataFrame(state['history'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.line(df, x='round', y=['revenue', 'profit'], 
                          title='Revenue vs Profit',
                          labels={'value': 'Amount ($)', 'round': 'Round'})
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.line(df, x='round', y=['occupancy', 'satisfaction'], 
                          title='Occupancy vs Satisfaction',
                          labels={'value': 'Percentage (%)', 'round': 'Round'})
            st.plotly_chart(fig2, use_container_width=True)

def show_competition():
    """Rekabet sayfası"""
    state = st.session_state.game_state
    
    st.markdown("## 🏆 Market Competition")
    st.markdown("---")
    
    # Rakip verilerini hazırla
    comp_data = competitors.copy()
    comp_data.append({
        'name': st.session_state.team_name,
        'market_share': state['market_share'],
        'satisfaction': state['customer_satisfaction']
    })
    
    df_comp = pd.DataFrame(comp_data)
    df_comp = df_comp.sort_values('market_share', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Market Share Comparison")
        fig1 = px.bar(df_comp, x='name', y='market_share', 
                     title='Market Share by Team',
                     color='market_share',
                     color_continuous_scale='blues')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("### 😊 Customer Satisfaction Comparison")
        fig2 = px.bar(df_comp, x='name', y='satisfaction', 
                     title='Customer Satisfaction by Team',
                     color='satisfaction',
                     color_continuous_scale='greens')
        st.plotly_chart(fig2, use_container_width=True)
    
    # Leaderboard
    st.markdown("### 🏅 Leaderboard")
    df_comp['rank'] = range(1, len(df_comp) + 1)
    st.dataframe(
        df_comp[['rank', 'name', 'market_share', 'satisfaction']],
        column_config={
            'rank': '🏅 Rank',
            'name': 'Team Name',
            'market_share': st.column_config.NumberColumn(
                'Market Share (%)',
                format="%.1f%%"
            ),
            'satisfaction': st.column_config.NumberColumn(
                'Satisfaction (%)',
                format="%.0f%%"
            )
        },
        hide_index=True,
        use_container_width=True
    )

# Main App
if not st.session_state.game_started:
    show_welcome_page()
else:
    # Sidebar Navigation
    with st.sidebar:
        st.markdown(f"### 🏨 {st.session_state.team_name}")
        st.markdown(f"**Round:** {st.session_state.current_round}")
        st.markdown(f"**Season:** {st.session_state.season}")
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "⚙️ Decisions", "📈 Results", "🏆 Competition"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("#### 💰 Quick Stats")
        state = st.session_state.game_state
        st.write(f"Cash: ${state['cash']/1000:.0f}k")
        st.write(f"Market Share: {state['market_share']:.1f}%")
        st.write(f"Share Price: ${state['share_price']:.2f}")
        
        st.markdown("---")
        
        if st.button("🔄 Reset Game", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main Content
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "⚙️ Decisions":
        show_decisions()
    elif page == "📈 Results":
        show_results()
    elif page == "🏆 Competition":
        show_competition()