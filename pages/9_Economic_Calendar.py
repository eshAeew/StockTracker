import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Economic Calendar | Indian Stock Market Analysis",
    page_icon="📅",
    layout="wide"
)

def main():
    st.title("Economic Calendar")
    st.write("Track important economic events and understand their market impact")
    
    # Date range selection
    st.sidebar.header("Date Range")
    today = datetime.datetime.now().date()
    
    # Default to showing next 30 days
    default_start_date = today
    default_end_date = today + datetime.timedelta(days=30)
    
    start_date = st.sidebar.date_input("Start Date", default_start_date)
    end_date = st.sidebar.date_input("End Date", default_end_date)
    
    if start_date > end_date:
        st.sidebar.error("End date must be after start date")
        return
    
    # Event type filter
    st.sidebar.header("Event Types")
    event_types = [
        "All Events",
        "Monetary Policy",
        "Economic Data",
        "Treasury Actions",
        "Earnings Season",
        "Index Changes",
        "Government Policy",
        "Global Events"
    ]
    
    selected_event_types = st.sidebar.multiselect(
        "Select Event Types",
        event_types,
        default=["All Events"]
    )
    
    # If "All Events" is selected, include everything
    if "All Events" in selected_event_types:
        selected_event_types = event_types[1:]  # All except "All Events"
    
    # Country filter
    st.sidebar.header("Countries")
    countries = ["India", "USA", "Europe", "China", "Japan"]
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        countries,
        default=["India"]
    )
    
    # Importance filter
    st.sidebar.header("Event Importance")
    importance_levels = [
        "High Impact",
        "Medium Impact",
        "Low Impact"
    ]
    
    selected_importance = st.sidebar.multiselect(
        "Select Importance Levels",
        importance_levels,
        default=importance_levels
    )
    
    # Get economic events
    events_df = get_economic_events(start_date, end_date)
    
    # Apply filters
    filtered_events = filter_events(
        events_df, 
        selected_event_types, 
        selected_countries, 
        selected_importance
    )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Upcoming Events", "Calendar View", "Important Events"])
        
        with tab1:
            if not filtered_events.empty:
                st.subheader(f"Upcoming Events ({len(filtered_events)} events found)")
                
                # Group by date
                grouped_events = filtered_events.groupby('Date')
                
                for date, events in grouped_events:
                    # Format date header
                    st.markdown(f"### {date.strftime('%A, %B %d, %Y')}")
                    
                    # Create a clean display for each event
                    for _, event in events.iterrows():
                        # Create an impact color
                        impact_colors = {
                            "High Impact": "🔴",
                            "Medium Impact": "🟠",
                            "Low Impact": "🟢"
                        }
                        
                        impact_color = impact_colors.get(event['Importance'], "⚪")
                        
                        # Expandable event details
                        with st.expander(f"{impact_color} {event['Time']} - {event['Event']} ({event['Country']})"):
                            st.markdown(f"**Type:** {event['Type']}")
                            st.markdown(f"**Previous Value:** {event['Previous']}")
                            st.markdown(f"**Forecast:** {event['Forecast']}")
                            st.markdown(f"**Potential Impact:** {event['Importance']}")
                            st.markdown(f"**Details:** {event['Description']}")
            else:
                st.info("No events found matching your criteria. Try adjusting your filters.")
        
        with tab2:
            st.subheader("Calendar View")
            
            if not filtered_events.empty:
                # Pivot the data for calendar view
                # Convert date column to string for stable grouping
                filtered_events_copy = filtered_events.copy()
                filtered_events_copy['Date_Str'] = filtered_events_copy['Date'].dt.strftime('%Y-%m-%d')
                
                # Group events by date string and create a combined description
                calendar_data = filtered_events_copy.groupby('Date_Str').apply(
                    lambda x: ", ".join(x['Event'].astype(str))
                ).reset_index()
                calendar_data.columns = ['Date_Str', 'Events']
                
                # Convert back to datetime for calendar view
                calendar_data['Date'] = pd.to_datetime(calendar_data['Date_Str'])
                
                # Create calendar visualization
                # We'll use a simple table for now
                calendar_data['Day'] = calendar_data['Date'].dt.day_name()
                calendar_data['Date_Formatted'] = calendar_data['Date'].dt.strftime('%b %d')
                
                # Create a calendar-like display
                start_of_week = start_date - datetime.timedelta(days=start_date.weekday())
                end_of_period = end_date + datetime.timedelta(days=(6 - end_date.weekday()))
                
                all_dates = pd.date_range(start=start_of_week, end=end_of_period)
                complete_calendar = pd.DataFrame({'Date': all_dates})
                complete_calendar['Day'] = complete_calendar['Date'].dt.day_name()
                complete_calendar['Date_Formatted'] = complete_calendar['Date'].dt.strftime('%b %d')
                
                # Merge with events
                complete_calendar = complete_calendar.merge(
                    calendar_data[['Date', 'Events']], 
                    on='Date', 
                    how='left'
                )
                
                # Replace NaN with empty string
                complete_calendar['Events'] = complete_calendar['Events'].fillna('')
                
                # Create weeks
                complete_calendar['Week'] = (complete_calendar['Date'] - start_of_week).dt.days // 7
                
                # For each week, create a subheader and show that week
                for week_num, week_data in complete_calendar.groupby('Week'):
                    week_start = week_data['Date_Formatted'].iloc[0]
                    week_end = week_data['Date_Formatted'].iloc[-1]
                    
                    st.markdown(f"#### Week of {week_start} to {week_end}")
                    
                    # Create a 7-column layout for days of week
                    cols = st.columns(7)
                    
                    # Show days of week as headers
                    for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
                        cols[i].markdown(f"**{day[:3]}**")
                    
                    # Show date and events
                    for i, (_, day_data) in enumerate(week_data.iterrows()):
                        day_col = cols[i]
                        
                        # Highlight current date
                        if day_data['Date'].date() == today:
                            day_col.markdown(f"**{day_data['Date_Formatted']}**")
                        else:
                            day_col.markdown(day_data['Date_Formatted'])
                        
                        # Show events if any
                        if day_data['Events']:
                            day_col.markdown(f"*{day_data['Events'][:20]}...*" if len(day_data['Events']) > 20 else f"*{day_data['Events']}*")
                    
                    st.markdown("---")
            else:
                st.info("No events found for calendar view.")
        
        with tab3:
            st.subheader("High Impact Events")
            
            # Filter for only high impact events
            high_impact_events = filtered_events[filtered_events['Importance'] == "High Impact"]
            
            if not high_impact_events.empty:
                # Create table
                display_cols = ['Date', 'Time', 'Country', 'Event', 'Previous', 'Forecast']
                
                # Format the date for display
                formatted_events = high_impact_events.copy()
                formatted_events['Date'] = formatted_events['Date'].dt.strftime('%b %d, %Y')
                
                st.table(formatted_events[display_cols])
                
                # Create impact visualization
                st.subheader("Impact Analysis")
                
                # Count events by type
                type_counts = high_impact_events['Type'].value_counts()
                
                fig = px.pie(
                    names=type_counts.index,
                    values=type_counts.values,
                    title="High Impact Events by Type",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No high impact events found in the selected period.")
    
    with col2:
        st.subheader("Market Impact Analysis")
        
        # Show events that have the highest potential market impact
        if not filtered_events.empty:
            # Create a heatmap showing event concentration
            # Convert date to string for stable groupby operation
            filtered_events_copy = filtered_events.copy()
            filtered_events_copy['Date_Str'] = filtered_events_copy['Date'].dt.strftime('%Y-%m-%d')
            event_counts = filtered_events_copy.groupby(['Date_Str', 'Type']).size().unstack().fillna(0)
            
            if not event_counts.empty and len(event_counts.columns) > 0:
                fig = px.imshow(
                    event_counts,
                    aspect="auto",
                    labels=dict(x="Event Type", y="Date", color="Number of Events"),
                    title="Event Concentration Heatmap",
                    color_continuous_scale="Viridis"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Show country distribution
            country_counts = filtered_events['Country'].value_counts()
            
            country_fig = px.bar(
                x=country_counts.index,
                y=country_counts.values,
                labels={'x': 'Country', 'y': 'Number of Events'},
                title="Events by Country",
                color=country_counts.values,
                color_continuous_scale=px.colors.sequential.Viridis
            )
            
            st.plotly_chart(country_fig, use_container_width=True)
            
            # Show upcoming critical events
            st.subheader("Critical Watch Events")
            critical_events = filtered_events[filtered_events['Importance'] == "High Impact"].head(5)
            
            if not critical_events.empty:
                for _, event in critical_events.iterrows():
                    with st.container():
                        st.markdown(f"**{event['Date'].strftime('%b %d, %Y')} - {event['Event']}**")
                        st.markdown(f"{event['Country']} | {event['Type']}")
                        st.markdown(f"Previous: {event['Previous']} | Forecast: {event['Forecast']}")
                        st.markdown("---")
            else:
                st.info("No critical events found in the selected period.")
            
            # Add a market sensitivity analysis
            st.subheader("Market Sensitivity")
            st.write("Sectors most sensitive to upcoming events:")
            
            # Sample data showing which sectors are sensitive to which events
            sensitivity_data = {
                "Banking": ["Monetary Policy", "Economic Data"],
                "IT": ["Global Events", "Treasury Actions"],
                "Pharma": ["Government Policy"],
                "Auto": ["Economic Data"],
                "FMCG": ["Economic Data", "Global Events"]
            }
            
            # Check which types of events are in the filtered set
            event_types_present = filtered_events['Type'].unique()
            
            # For each sector, calculate a sensitivity score based on event types present
            sensitivity_scores = {}
            
            for sector, sensitive_to in sensitivity_data.items():
                # Calculate how many of the sensitive event types are present
                overlap = len(set(sensitive_to) & set(event_types_present))
                
                # Calculate a score (0-100)
                if len(sensitive_to) > 0:
                    score = (overlap / len(sensitive_to)) * 100
                else:
                    score = 0
                
                sensitivity_scores[sector] = score
            
            # Create a gauge chart for each sector
            for sector, score in sensitivity_scores.items():
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    title={'text': sector},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 30], 'color': "green"},
                            {'range': [30, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "red"}
                        ]
                    }
                ))
                
                fig.update_layout(height=200, margin=dict(l=10, r=10, t=50, b=10))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No events available for impact analysis.")
            
        # Add expert insights
        st.subheader("Expert Insights")
        st.markdown("""
        **Key takeaways for the selected period:**
        
        1. Watch for RBI monetary policy decisions which may impact banking and financial sectors
        2. International trade data may influence export-oriented sectors
        3. Quarterly GDP numbers could drive market sentiment
        4. Budget-related announcements might cause sector-specific movements
        """)

def get_economic_events(start_date, end_date):
    """
    Get economic events for the given date range
    In a real app, this would fetch from an API
    """
    # Sample data for demonstration
    today = datetime.datetime.now().date()
    
    # Generate a range of dates
    date_range = pd.date_range(start=start_date, end=end_date)
    
    # Economic event types
    event_types = [
        "Monetary Policy",
        "Economic Data",
        "Treasury Actions",
        "Earnings Season",
        "Index Changes",
        "Government Policy",
        "Global Events"
    ]
    
    # Specific events for each type
    event_details = {
        "Monetary Policy": [
            "RBI Interest Rate Decision",
            "RBI Monetary Policy Minutes",
            "Fed Interest Rate Decision",
            "ECB Interest Rate Decision",
            "Bank of Japan Policy Statement"
        ],
        "Economic Data": [
            "GDP Growth Rate",
            "CPI Inflation",
            "Unemployment Rate",
            "Industrial Production",
            "Retail Sales",
            "Trade Balance",
            "Manufacturing PMI",
            "Services PMI"
        ],
        "Treasury Actions": [
            "T-Bill Auction",
            "Government Bond Auction",
            "Foreign Reserves",
            "Fiscal Deficit",
            "Government Spending"
        ],
        "Earnings Season": [
            "Major Banks Earnings",
            "IT Sector Earnings",
            "Auto Sector Earnings",
            "FMCG Sector Earnings",
            "Pharma Sector Earnings"
        ],
        "Index Changes": [
            "Nifty Index Rebalancing",
            "Sensex Rebalancing",
            "MSCI Index Changes",
            "FTSE Index Changes"
        ],
        "Government Policy": [
            "Budget Announcement",
            "Tax Policy Changes",
            "Subsidy Announcements",
            "Import/Export Regulations",
            "FDI Policy Changes"
        ],
        "Global Events": [
            "G20 Summit",
            "OPEC Meeting",
            "US-China Trade Talks",
            "Brexit Developments",
            "IMF Economic Outlook"
        ]
    }
    
    # Countries
    countries = ["India", "USA", "Europe", "China", "Japan"]
    
    # Importance levels
    importance_levels = ["High Impact", "Medium Impact", "Low Impact"]
    
    # Create random events for the date range
    events = []
    
    np.random.seed(42)  # For reproducible results
    
    # Generate approximately 2-3 events per day
    for date in date_range:
        # Number of events for this day (1-4)
        num_events = np.random.randint(1, 5)
        
        for _ in range(num_events):
            # Randomly select an event type
            event_type = np.random.choice(event_types)
            
            # Randomly select a specific event of that type
            event = np.random.choice(event_details[event_type])
            
            # Randomly select a country
            country = np.random.choice(countries)
            
            # Randomly select an importance level
            importance = np.random.choice(
                importance_levels, 
                p=[0.2, 0.5, 0.3]  # Probability distribution for importance levels
            )
            
            # Generate a random time for the event
            hour = np.random.randint(8, 18)
            minute = np.random.choice([0, 15, 30, 45])
            time_str = f"{hour:02d}:{minute:02d}"
            
            # Generate random previous and forecast values (for numeric indicators)
            previous = None
            forecast = None
            
            if "Rate" in event or "Growth" in event or "Inflation" in event:
                previous = f"{np.random.uniform(-2, 8):.2f}%"
                forecast = f"{np.random.uniform(-2, 8):.2f}%"
            elif "Production" in event or "Sales" in event:
                previous = f"{np.random.uniform(-5, 10):.2f}%"
                forecast = f"{np.random.uniform(-5, 10):.2f}%"
            elif "Balance" in event or "Deficit" in event:
                previous = f"${np.random.randint(-100, 100)} B"
                forecast = f"${np.random.randint(-100, 100)} B"
            elif "Reserves" in event:
                previous = f"${np.random.randint(300, 600)} B"
                forecast = f"${np.random.randint(300, 600)} B"
            
            # Generate a description
            description = f"This {event_type.lower()} event may impact markets, particularly the {np.random.choice(['banking', 'IT', 'pharma', 'auto', 'energy'])} sector. Analysts are closely watching for signs of {'positive' if np.random.random() > 0.5 else 'negative'} trends."
            
            events.append({
                "Date": date,
                "Time": time_str,
                "Event": event,
                "Type": event_type,
                "Country": country,
                "Importance": importance,
                "Previous": previous,
                "Forecast": forecast,
                "Description": description
            })
    
    # Add specific important events
    
    # RBI Policy (if within range)
    rbi_date = today.replace(day=1) + datetime.timedelta(days=7)  # Around 8th of month
    if start_date <= rbi_date <= end_date:
        events.append({
            "Date": rbi_date,
            "Time": "11:45",
            "Event": "RBI Interest Rate Decision",
            "Type": "Monetary Policy",
            "Country": "India",
            "Importance": "High Impact",
            "Previous": "6.50%",
            "Forecast": "6.50%",
            "Description": "The Reserve Bank of India (RBI) announces its interest rate decision. This is a crucial event that impacts the banking sector and overall market sentiment. Analysts expect rates to remain unchanged due to inflation concerns."
        })
    
    # GDP Data (if within range)
    gdp_date = today.replace(day=15) + datetime.timedelta(days=15)  # Around end of month
    if start_date <= gdp_date <= end_date:
        events.append({
            "Date": gdp_date,
            "Time": "17:30",
            "Event": "GDP Growth Rate",
            "Type": "Economic Data",
            "Country": "India",
            "Importance": "High Impact",
            "Previous": "7.8%",
            "Forecast": "7.3%",
            "Description": "Quarterly GDP growth figures will be released. This is a key indicator of economic health and will influence market direction. A figure above 7% is generally considered positive for Indian markets."
        })
    
    # Budget related (if in Feb)
    budget_date = datetime.date(today.year, 2, 1)
    if start_date <= budget_date <= end_date:
        events.append({
            "Date": budget_date,
            "Time": "11:00",
            "Event": "Union Budget Presentation",
            "Type": "Government Policy",
            "Country": "India",
            "Importance": "High Impact",
            "Previous": None,
            "Forecast": None,
            "Description": "The annual Union Budget will be presented in Parliament. This will outline the government's fiscal policy, taxation changes, and spending priorities for the coming year. Markets typically show high volatility during this event."
        })
    
    return pd.DataFrame(events)

def filter_events(df, event_types, countries, importance_levels):
    """Filter events based on selected criteria"""
    filtered_df = df.copy()
    
    # Apply event type filter if not empty
    if event_types:
        filtered_df = filtered_df[filtered_df['Type'].isin(event_types)]
    
    # Apply country filter if not empty
    if countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(countries)]
    
    # Apply importance filter if not empty
    if importance_levels:
        filtered_df = filtered_df[filtered_df['Importance'].isin(importance_levels)]
    
    # Convert dates to strings for stable sorting
    filtered_df['Date_Str'] = filtered_df['Date'].dt.strftime('%Y-%m-%d')
    
    # Sort by date string and time
    filtered_df = filtered_df.sort_values(['Date_Str', 'Time'])
    
    # Drop the temporary sort column
    filtered_df = filtered_df.drop('Date_Str', axis=1)
    
    return filtered_df

if __name__ == "__main__":
    main()