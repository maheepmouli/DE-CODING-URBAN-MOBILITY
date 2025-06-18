import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
import io
import json
import geopandas as gpd
from keplergl import KeplerGl
import base64  # For downloading data as base64 encoded link
from datetime import timedelta  # Import timedelta for date calculations
import re  # Import regular expressions for column matching

# Import Plotly for interactive plots
import plotly.express as px
import plotly.graph_objects as go

# --- Encode LOGO.jpg to base64 ---
# Ensure 'LOGO.png' is in the same directory as your app.py
try:
    with open("LOGO.png", "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
except FileNotFoundError:
    st.error("LOGO.png not found. Please ensure the logo file is in the correct directory.")
    logo_base64 = "" # Fallback to empty string if not found

# --- Streamlit Setup ---
# Set page configuration with title, wide layout, and a favicon
st.set_page_config(page_title="FlowSIGHT - Congestion Analytic Assistant", layout="wide", page_icon="🚦")

# --- Custom CSS for themes ---
# Define CSS for both dark and light modes to ensure consistent styling
DARK_MODE_CSS = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;700&display=swap'); /* Using Quicksand for playful feel */

    /* ======================================================================
       1) General Theme & Background (Darker Theme)
    ====================================================================== */
    html, body, [class*="st-"], .stApp {{
      font-family: 'Quicksand', sans-serif;
      background-color: #1A1A1A; /* Very dark background */
      color: #F5F5F5; /* Light text for readability on dark background */
    }}

    /* Primary text color for all elements */
    .stApp, .stApp *, .css-18e3th9, .css-1d391kg, .st-emotion-cache-1y4p8pa {{
        color: #F5F5F5 !important; /* Light text */
    }}

    /* Custom Header Container for Title and Logo */
    .header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-right: 15px;
    }}

    .gradient-title {{
        background: linear-gradient(to right, #A700FF, #00D4FF); /* Vibrant Purple to Cyan/Blue gradient */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3em;
        font-weight: 700;
        text-shadow: none;
        margin: 0;
        line-height: 1.2;
    }}

    .header-logo {{
        height: 250px; /* Adjusted height for dark mode logo */
        width: auto;
        border-radius: 8px;
        object-fit: contain;
    }}

    /* Title styling for other sections (h2, h3) */
    h2, h3 {{
        color: #00D4FF !important; /* Vibrant blue for section headers */
        font-weight: 700 !important; /* Make main content headers thicker */
        text-shadow: none;
    }}

    /* ======================================================================
       2) Sidebar Styling
    ====================================================================== */
    [data-testid="stSidebar"] {{
        background-color: #2A2A2A !important; /* Slightly lighter dark grey for sidebar */
        position: relative; /* Needed for pseudo-element positioning */
        border-right: none; /* Remove existing solid border */
    }}
    [data-testid="stSidebar"]::after {{
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 3px; /* Thickness of the gradient border */
        height: 100%;
        background: linear-gradient(to bottom, #7C4DFF, #00D4FF); /* More dim gradient for sidebar */
        z-index: 1; /* Ensure it's on top */
    }}

    [data-testid="stSidebar"] *, [data-testid="stSidebar"] .st-emotion-cache-1g6gooi {{
      color: #F5F5F5 !important; /* Light text */
    }}

    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: #7C4DFF !important; /* More dim purple for sidebar headers */
        font-weight: 700 !important; /* Make sidebar headers thicker */
    }}

    /* Sidebar input/textarea styling */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] .st-b8 {{ /* for multiselect */
      color: #F5F5F5 !important; /* Light text in inputs */
      background-color: #3A3A3A; /* Slightly lighter dark for inputs */
      border: 0.8px solid #555555;
      border-radius: 15px;
    }}
    
    /* Prompt Guide Text Styling */
    .prompt-guide-text p {{
        font-size: 0.9em !important;
        line-height: 1.4;
        margin-bottom: 3px;
        font-weight: 500;
        color: #CCCCCC; /* Slightly subdued text for guide */
    }}
    .prompt-guide-text strong {{
        font-size: 1.0em !important;
        font-weight: 700;
        color: #00D4FF !important; /* Highlight prompt guide header with vibrant blue */
    }}

    /* ======================================================================
       3) Widget Styling (Sliders, Buttons, etc.)
    ====================================================================== */
    /* Slider thumb and track styling */
    input[type="range"]::-webkit-slider-thumb {{
      background-color: #7C4DFF !important; /* More dim purple */
      border: 3px solid #F5F5F5 !important; /* White border for contrast */
      width: 18px !important;
      height: 18px !important;
      box-shadow: 0 0 10px rgba(124, 77, 255, 0.5);
      -webkit-appearance: none; /* Make cursor button visible */
      appearance: none;
      cursor: pointer; /* Make cursor button visible */
    }}

    input[type="range"]::-webkit-slider-runnable-track {{
      background: linear-gradient(to right, #7C4DFF, #00D4FF) !important; /* More dim Purple to Cyan/Blue gradient */
      height: 8px !important;
    }}

    /* Buttons */
    .stButton>button, .stDownloadButton>button {{
        border: 2px solid #00D4FF !important; /* Vibrant blue border */
        background-color: transparent !important;
        color: #F5F5F5 !important; /* Light text */
        border-radius: 15px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 212, 255, 0.1);
    }}

    .stButton>button:hover, .stDownloadButton>button:hover {{
        background-color: #00D4FF !important; /* Vibrant blue on hover */
        color: #1A1A1A !important; /* Dark text on hover */
        box-shadow: 0 6px 12px rgba(0, 212, 255, 0.5);
        transform: translateY(-2px);
    }}

    /* Checkbox */
    .stCheckbox {{
        border: 0.8px solid #555555;
        background-color: rgba(0, 212, 255, 0.05); /* Light blue tint */
        border-radius: 15px;
        padding: 5px 10px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }}

    /* ======================================================================
       4) Main Content & Data Display
    ====================================================================== */
    hr.main-separator {{
      border: none; /* Remove default border */
      height: 3px; /* Make it a bit thicker */
      background: linear-gradient(to right, #7C4DFF, #00D4FF); /* More dim gradient */
      opacity: 0.9; /* Make it more opaque */
      margin: 32px 0;
      border-radius: 5px; /* Soften edges */
    }}
    
    /* Custom styling for dataframes */
    .stDataFrame {{
        border: 0.8px solid #555555 !important;
        background-color: rgba(255, 167, 38, 0.03); /* Very light orange tint */
        color: #F5F5F5 !important; /* Light text */
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }}

    .stDataFrame div[data-testid="stTable"] {{
        color: #F5F5F5 !important; /* Ensure table text is light */
    }}

    .stDataFrame table {{
        border-collapse: collapse;
    }}

    .stDataFrame th {{
        background-color: #3A3A3A !important; /* Darker grey for headers */
        color: #F5F5F5 !important; /* Light header font */
        border: 0.8px solid #555555 !important;
        font-weight: 700; /* Make table headers bold */
    }}

    .stDataFrame td {{
        border: 0.8px solid #444444 !important;
        color: #F5F5F5 !important; /* Light text for cells */
    }}


    /* Metric styling */
    .stMetric {{
        background: linear-gradient(135deg, rgba(124, 77, 255, 0.05), rgba(0, 212, 255, 0.05)); /* Subtle gradient background with new colors */
        border: 1.5px solid #555555; /* Slightly thicker and clearer border */
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0, 212, 255, 0.15), 0 0 10px rgba(124, 77, 255, 0.05); /* Blue glow + subtle purple hint */
        transition: transform 0.2s ease-in-out;
    }}
    .stMetric:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0, 212, 255, 0.3), 0 0 15px rgba(124, 77, 255, 0.1); /* Stronger glow */
    }}
    .stMetric [data-testid="stMetricLabel"] {{
        color: #FFA726 !important; /* Metric label color - vibrant orange */
        font-weight: 700;
    }}
    .stMetric [data-testid="stMetricValue"] {{
        color: #F5F5F5 !important; /* Light value color */
        font-size: 2.2em; /* Even larger value font */
        font-weight: 700; /* Make metric values bold */
    }}
    .stMetric [data-testid="stMetricDelta"] {{
        color: #4CAF50 !important; /* Green for delta values (unchanged for standard feedback) */
        font-weight: 600;
    }}


    /* Expander styling */
    .st-expander, .st-emotion-cache-0 {{
        border: 0.8px solid #444444 !important;
        border-radius: 15px !important;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    .st-expander header, .st-emotion-cache-1r6slb0 {{
        background-color: #2A2A2A !important; /* Dark grey for expander header */
        font-weight: 600;
        color: #00D4FF !important; /* Vibrant blue for expander header text */
    }}

    /* Info/Warning/Error boxes */
    .stAlert {{
        border-radius: 15px;
        border: 0.8px solid;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }}
    .st-emotion-cache-4oy321 {{ /* Info box (using vibrant blue) */
        border-color: #00D4FF;
        background-color: rgba(0, 212, 255, 0.1);
        color: #F5F5F5 !important;
    }}
    .st-emotion-cache-l91u7h {{ /* Warning box (using vibrant orange) */
        border-color: #FFA726;
        background-color: rgba(255, 167, 38, 0.1);
        color: #F5F5F5 !important;
    }}
    .st-emotion-cache-1wivapv {{ /* Error box (using red) */
        border-color: #F44336;
        background-color: rgba(244, 67, 54, 0.1);
        color: #F5F5F5 !important;
    }}

    /* Card styling for City Traffic Snapshots */
    .city-card {{
        background: linear-gradient(135deg, rgba(124, 77, 255, 0.03), rgba(0, 212, 255, 0.03)); /* Subtle gradient background */
        border: 1.5px solid #444444; /* Slightly thicker and clearer border */
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15), 0 0 10px rgba(124, 77, 255, 0.05); /* General dark shadow + purple glow */
        transition: transform 0.2s ease-in-out;
    }}
    .city-card:hover {{
        transform: translateY(-8px) rotate(-1deg);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25), 0 0 20px rgba(0, 212, 255, 0.1); /* Stronger shadow + blue glow */
    }}
    .city-card h3 {{
        color: #FFA726 !important; /* Vibrant orange for card titles */
        text-shadow: none;
        border-bottom: 0.8px solid #444444;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }}
    .city-card strong {{
        color: #F5F5F5; /* Light text for bold labels inside cards */
        font-weight: 700;
    }}
    .city-card p {{
        margin-bottom: 5px;
        color: #CCCCCC; /* Slightly subdued text for readability */
    }}

    </style>
"""

LIGHT_MODE_CSS = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;700&display=swap');

    html, body, [class*="st-"], .stApp {{
      font-family: 'Quicksand', sans-serif;
      background-color: #F0F2F6; /* Light background */
      color: #333333; /* Dark text */
    }}

    .stApp, .stApp *, .css-18e3th9, .css-1d391kg, .st-emotion-cache-1y4p8pa {{
        color: #333333 !important; /* Dark text */
    }}

    .gradient-title {{
        background: linear-gradient(to right, #4CAF50, #2196F3); /* Green to Blue gradient */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3em; /* Adjusted font size for light mode title */
        font-weight: 700;
        text-shadow: none;
        margin: 0;
        line-height: 1.2;
    }}

    .header-logo {{
        height: 150px; /* Kept height for light mode logo */
        width: auto;
        border-radius: 8px;
        object-fit: contain;
    }}

    h2, h3 {{
        color: #2196F3 !important; /* Blue for section headers */
        font-weight: 700 !important;
        text-shadow: none;
    }}

    [data-testid="stSidebar"] {{
        background-color: #E0E4EB !important; /* Slightly darker light grey for sidebar */
        position: relative;
        border-right: none;
    }}
    [data-testid="stSidebar"]::after {{
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 3px;
        height: 100%;
        background: linear-gradient(to bottom, #4CAF50, #2196F3); /* Green to Blue gradient */
        z-index: 1;
    }}

    [data-testid="stSidebar"] *, [data-testid="stSidebar"] .st-emotion-cache-1g6gooi {{
      color: #333333 !important; /* Dark text */
    }}

    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: #4CAF50 !important; /* Green for sidebar headers */
        font-weight: 700 !important;
    }}

    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] .st-b8 {{
      color: #333333 !important;
      background-color: #FFFFFF;
      border: 0.8px solid #CCCCCC;
      border-radius: 15px;
    }}
    
    .prompt-guide-text p {{
        color: #666666;
    }}
    .prompt-guide-text strong {{
        color: #2196F3 !important;
    }}

    input[type="range"]::-webkit-slider-thumb {{
      background-color: #4CAF50 !important; /* Green */
      border: 3px solid #FFFFFF !important;
      box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
    }}

    input[type="range"]::-webkit-slider-runnable-track {{
      background: linear-gradient(to right, #4CAF50, #2196F3) !important;
    }}

    .stButton>button, .stDownloadButton>button {{
        border: 2px solid #2196F3 !important;
        background-color: transparent !important;
        color: #333333 !important;
        border-radius: 15px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(33, 150, 243, 0.1);
    }}

    .stButton>button:hover, .stDownloadButton>button:hover {{
        background-color: #2196F3 !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 12px rgba(33, 150, 243, 0.5);
    }}

    .stCheckbox {{
        border: 0.8px solid #CCCCCC;
        background-color: rgba(33, 150, 243, 0.05);
        border-radius: 15px;
        padding: 5px 10px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }}

    hr.main-separator {{
      background: linear-gradient(to right, #4CAF50, #2196F3);
    }}
    
    .stDataFrame {{
        border: 0.8px solid #CCCCCC !important;
        background-color: rgba(255, 152, 0, 0.03); /* Light orange tint */
        color: #333333 !important;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }}

    .stDataFrame div[data-testid="stTable"] {{
        color: #333333 !important;
    }}

    .stDataFrame table {{
        border-collapse: collapse;
    }}

    .stDataFrame th {{
        background-color: #D3D8E0 !important;
        color: #333333 !important;
        border: 0.8px solid #CCCCCC !important;
    }}

    .stDataFrame td {{
        border: 0.8px solid #E0E4EB !important;
        color: #333333 !important;
    }}

    .stMetric {{
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.05), rgba(33, 150, 243, 0.05));
        border: 1.5px solid #CCCCCC;
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.15), 0 0 10px rgba(76, 175, 80, 0.05);
    }}
    .stMetric:hover {{
        box-shadow: 0 8px 20px rgba(33, 150, 243, 0.3), 0 0 15px rgba(76, 175, 80, 0.1);
    }}
    .stMetric [data-testid="stMetricLabel"] {{
        color: #FF9800 !important; /* Orange */
    }}
    .stMetric [data-testid="stMetricValue"] {{
        color: #333333 !important;
    }}
    .stMetric [data-testid="stMetricDelta"] {{
        color: #4CAF50 !important;
    }}

    .st-expander, .st-emotion-cache-0 {{
        border: 0.8px solid #CCCCCC !important;
        border-radius: 15px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    .st-expander header, .st-emotion-cache-1r6slb0 {{
        background-color: #E0E4EB !important;
        color: #2196F3 !important;
    }}

    .stAlert {{
        border-radius: 15px;
        border: 0.8px solid;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }}
    .st-emotion-cache-4oy321 {{
        border-color: #2196F3;
        background-color: rgba(33, 150, 243, 0.1);
        color: #333333 !important;
    }}
    .st-emotion-cache-l91u7h {{
        border-color: #FF9800;
        background-color: rgba(255, 152, 0, 0.1);
        color: #333333 !important;
    }}
    .st-emotion-cache-1wivapv {{
        border-color: #F44336;
        background-color: rgba(244, 67, 54, 0.1);
        color: #333333 !important;
    }}

    .city-card {{
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.03), rgba(33, 150, 243, 0.03));
        border: 1.5px solid #CCCCCC;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15), 0 0 10px rgba(76, 175, 80, 0.05);
    }}
    .city-card:hover {{
        transform: translateY(-8px) rotate(-1deg);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25), 0 0 20px rgba(33, 150, 243, 0.1);
    }}
    .city-card h3 {{
        color: #FF9800 !important;
        text-shadow: none;
        border-bottom: 0.8px solid #CCCCCC;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }}
    .city-card strong {{
        color: #333333;
    }}
    .city-card p {{
        color: #666666;
    }}
    </style>
"""

# Theme Toggle in Sidebar
st.sidebar.subheader("App Theme")
use_light_mode = st.sidebar.checkbox("Enable Light Mode", value=False)

if use_light_mode:
    st.markdown(LIGHT_MODE_CSS, unsafe_allow_html=True)
    plotly_template = "plotly_white" # Use light template for Plotly
else:
    st.markdown(DARK_MODE_CSS, unsafe_allow_html=True)
    plotly_template = "plotly_dark" # Use dark template for Plotly


# --- Custom App Title with Logo ---
st.markdown(
    f"""
    <div class="header-container">
        <h1 class="gradient-title">FlowSIGHT - Congestion Analytic Assistant</h1>
        <img src="data:image/jpeg;base64,{logo_base64}" class="header-logo" alt="FlowSIGHT Logo" onerror="this.onerror=null;this.src='https://placehold.co/80x80/FFFFFF/333333?text=Logo';">
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
#                              LOAD DATA FUNCTIONS
# =============================================================================
# Cache data loading to improve performance on re-runs
@st.cache_data
def load_data(file_path="city_data.csv"):
    """
    Loads city traffic data from a CSV file.
    Performs critical column checks and data type conversions.
    """
    try:
        df = pd.read_csv(file_path)
        critical_cols = ['CITY', 'date', 'congestion_index', 'AQI_mean',
                         'MANAGEMENT_TYPE', 'SPEED', 'prcp', 'wspd', 'tavg',
                         'POPULATION DENSITY', 'TOTAL PUBLIC TRANSPORT TRIP', 'tmin', 'tmax']

        if 'Holiday_Flag' in df.columns:
            critical_cols.append('Holiday_Flag')
            df['Holiday_Flag'] = df['Holiday_Flag'].astype(bool)
        else:
            st.warning("The 'Holiday_Flag' column was not found in 'city_data.csv'. Holiday analysis features will be unavailable.")

        missing_critical_cols = [col for col in critical_cols if col not in df.columns]
        if missing_critical_cols:
            st.error(f"Missing critical columns: {', '.join(missing_critical_cols)}. Please ensure your CSV contains these columns.")
            return None

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date'], inplace=True) # Drop rows where date conversion failed

        if 'CITY' in df.columns:
            df['CITY'] = df['CITY'].str.upper()
            df['CITY'] = df['CITY'].replace('LOS ANGELOS', 'LOS ANGELES') # Data cleaning for consistency

        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please ensure 'city_data.csv' is in the correct directory.")
        return None
    except Exception as e:
        st.error(f"Data loading error: {e}")
        return None

# Cache policy data loading as well
@st.cache_data
def load_policy_data(file_path="combined_traffic_policies_with_city.csv"):
    """
    Loads traffic policy data from a CSV file.
    Performs data type conversions and column renaming for consistency.
    """
    try:
        df_policies = pd.read_csv(file_path)
        df_policies['Date'] = pd.to_datetime(df_policies['Date'], errors='coerce')
        df_policies.dropna(subset=['Date', 'city'], inplace=True) # Drop rows with missing date or city

        # Rename 'city' column to 'CITY' for consistency with main data
        if 'city' in df_policies.columns:
            df_policies.rename(columns={'city': 'CITY'}, inplace=True)
        if 'CITY' in df_policies.columns:
            df_policies['CITY'] = df_policies['CITY'].str.upper()

        return df_policies
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please ensure 'combined_traffic_policies_with_city.csv' is in the correct directory.")
        return None
    except Exception as e:
        st.error(f"Policy data loading error: {e}. Check column names like 'Date' and 'city'.")
        return None

# Load the datasets
df_original = load_data()
df_policies = load_policy_data()

# Stop the app if main data fails to load
if df_original is None:
    st.stop()
df = df_original.copy() # Create a mutable copy for filtering


# =============================================================================
#                                SIDEBAR
# =============================================================================
st.sidebar.header("Settings & Queries")

st.sidebar.subheader("Data Filters")

# Use st.container for a visual grouping of filters
with st.sidebar.container(border=True):
    st.markdown("##### Environmental Filters")
    # ----------------- Filter 1: Temperature Threshold -----------------
    min_tavg, max_tavg = float(df_original['tavg'].min()), float(df_original['tavg'].max())
    temp_threshold = st.slider( # Using st.slider directly here
        "Average Temperature (°C)",
        min_value=min_tavg,
        max_value=max_tavg,
        value=(min_tavg, max_tavg),
        step=0.1
    )
    df = df[(df['tavg'] >= temp_threshold[0]) & (df['tavg'] <= temp_threshold[1])]

    # ----------------- Filter 2: Precipitation Threshold -----------------
    min_prcp, max_prcp = float(df_original['prcp'].min()), float(df_original['prcp'].max())
    prcp_threshold = st.slider( # Using st.slider directly here
        "Precipitation (mm)",
        min_value=min_prcp,
        max_value=max_prcp,
        value=(min_prcp, max_prcp),
        step=0.1
    )
    df = df[(df['prcp'] >= prcp_threshold[0]) & (df['prcp'] <= prcp_threshold[1])]

    # ----------------- NEW Filter 4: Mean AQI Threshold -----------------
    if 'AQI_mean' in df_original.columns:
        min_aqi, max_aqi = float(df_original['AQI_mean'].min()), float(df_original['AQI_mean'].max())
        aqi_threshold = st.slider( # Using st.slider directly here
            "Mean AQI",
            min_value=min_aqi,
            max_value=max_aqi,
            value=(min_aqi, max_aqi),
            step=1.0
        )
        df = df[(df['AQI_mean'] >= aqi_threshold[0]) & (df['AQI_mean'] <= aqi_threshold[1])]
    else:
        st.warning("AQI_mean column not found for filtering.")

# Insert a thin separator in sidebar
st.sidebar.markdown('<hr style="border-top:0.8px solid #444444;" />', unsafe_allow_html=True)

with st.sidebar.container(border=True):
    st.markdown("##### Traffic & Transport Filters")
    # ----------------- Filter 3: Management Type -----------------
    all_management_types = df_original['MANAGEMENT_TYPE'].unique().tolist()
    selected_management_types = st.multiselect( # Using st.multiselect directly here
        "Traffic Management Type",
        options=all_management_types,
        default=all_management_types
    )
    df = df[df['MANAGEMENT_TYPE'].isin(selected_management_types)]

    # ----------------- NEW Filter 5: Public Transport Frequency -----------------
    if 'TOTAL PUBLIC TRANSPORT TRIP' in df_original.columns:
        min_pt_trips, max_pt_trips = float(df_original['TOTAL PUBLIC TRANSPORT TRIP'].min()), float(df_original['TOTAL PUBLIC TRANSPORT TRIP'].max())
        pt_trips_threshold = st.slider( # Using st.slider directly here
            "Total Public Transport Trips (per day)",
            min_value=min_pt_trips,
            max_value=max_pt_trips,
            value=(min_pt_trips, max_pt_trips),
            step=100.0
        )
        df = df[(df['TOTAL PUBLIC TRANSPORT TRIP'] >= pt_trips_threshold[0]) & (df['TOTAL PUBLIC TRANSPORT TRIP'] <= pt_trips_threshold[1])]
    else:
        st.warning("TOTAL PUBLIC TRANSPORT TRIP column not found for filtering.")

# Insert another separator before the “Ask me anything” section
st.sidebar.markdown('<hr style="border-top:0.8px solid #444444;" />', unsafe_allow_html=True)

st.sidebar.subheader("Ask me anything")
# Add a prompt guide with reduced font size
st.sidebar.markdown(
    """
    <div class="prompt-guide-text">
    <strong>Prompt Guide (Sample Questions):</strong>
    <p>&bull; "Show congestion trend in LONDON"</p>
    <p>&bull; "What is the correlation between AQI and congestion in PARIS?"</p>
    <p>&bull; "Compare speed in BARCELONA and NEW YORK CITY"</p>
    <p>&bull; "Rank cities by public transport trips"</p>
    <p>&bull; "Show distribution of speed by management type"</p>
    <p>&bull; "What is the strongest factor affecting congestion?"</p>
    <p>&bull; "Show correlation heatmap"</p>
    <p>&bull; "Is congestion affected by holidays?"</p>
    </div>
    """,
    unsafe_allow_html=True
)

user_query = st.sidebar.text_area("Your Question:", "Compare congestion in BARCELONA and LONDON", height=100)
gemini_api_key = st.sidebar.text_input("Your Gemini API Key", type="password", placeholder="Enter your Gemini API Key")

# =============================================================================
#                        MAIN‐AREA: INITIAL CHECKS & HOME PAGE
# =============================================================================
if df.empty:
    st.warning("No data available after applying filters. Please adjust your filter selections.")
    st.stop()

# -------------------- Separator before “City Congestion Ranking” --------------------
st.markdown('<hr class="main-separator" />', unsafe_allow_html=True)

# Wrap "City Congestion Ranking" in a container
with st.container(border=True):
    st.header("City Congestion Ranking (Overall)")
    if not df.empty:
        avg_congestion_overall = df.groupby("CITY")["congestion_index"].mean().sort_values(ascending=False).reset_index()

        # REVERTED: Use highlight functions for min/max instead of a gradient
        def highlight_max(s):
            is_max = s == s.max()
            return ['background-color: #00D4FF; color: #1A1A1A;' if v else '' for v in is_max] # Vibrant blue for max, dark text
        
        def highlight_min(s):
            is_min = s == s.min()
            return ['background-color: #7C4DFF; color: #F5F5F5;' if v else '' for v in is_min] # More dim purple for min, light text

        st.dataframe(
            avg_congestion_overall.style.apply(highlight_max, subset=['congestion_index'])
                                         .apply(highlight_min, subset=['congestion_index']),
            hide_index=True,
            use_container_width=True
        )
        st.markdown("*(Higher congestion index means more congested)*")
    else:
        st.info("No data available to display city rankings after applying filters.")

# -------------------- Separator before “City Traffic Snapshots” --------------------
st.markdown('<hr class="main-separator" />', unsafe_allow_html=True)

if st.sidebar.checkbox("Show City Snapshots (based on filtered data)"):
    # Wrap "City Traffic Snapshots" in a container
    with st.container(border=True):
        st.header("City Traffic Snapshots")
        if not df.empty:
            if 'date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['date']):
                df['year_month'] = df['date'].dt.to_period('M')
            else:
                st.warning("Date column not found or not in datetime format for city snapshots. Skipping monthly aggregation.")

            city_summary = df.groupby('CITY').agg({
                'congestion_index': 'mean',
                'tavg': 'mean',
                'prcp': 'mean',
                'AQI_mean': 'mean',
                'TOTAL PUBLIC TRANSPORT TRIP': 'mean',
                'POPULATION DENSITY': 'mean'
            }).reset_index()

            # Display snapshots as cards using st.columns for a grid layout
            cols = st.columns(3) # Create 3 columns for card layout
            for i, (_, row) in enumerate(city_summary.iterrows()):
                with cols[i % 3]: # Cycle through columns (0, 1, 2, 0, 1, 2...)
                    st.markdown(f"""
                    <div class="city-card">
                        <h3>{row['CITY']} - Traffic Snapshot</h3>
                        <p><strong>Population Density</strong>: {int(row['POPULATION DENSITY']):,} people/km²</p>
                        <p><strong>Avg. Temperature</strong>: {row['tavg']:.1f}°C</p>
                        <p><strong>Rainfall</strong>: {row['prcp']:.0f} mm/month</p>
                        <p><strong>Average AQI</strong>: {row['AQI_mean']:.0f}</p>
                        <p><strong>Public Transport Use</strong>: {row['TOTAL PUBLIC TRANSPORT TRIP']:.0f} trips/day</p>
                        <p><strong>Average Congestion Index</strong>: {row['congestion_index']:.0f}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No data to display city snapshots after applying filters.")

# =============================================================================
#                             CORE FUNCTION
# =============================================================================
def plot_and_answer(query, data_frame, plot_template):
    """
    Analyzes the user query and generates appropriate Plotly visualizations
    and textual responses based on the filtered data.
    """
    # This function now exclusively uses Plotly, so Matplotlib/Seaborn styling is removed.
    query_lower = query.lower()
    plot_generated = False # Flag to track if a Plotly figure was generated
    fig = None # Kept for compatibility in case a Matplotlib plot is ever re-introduced
    default_plot_height = 800 # Define a default height for plots
    font_color = "white" if plot_template == "plotly_dark" else "black" # Set font color based on theme

    # 1. Trend over time (Plotly Line Chart)
    if "trend" in query_lower or "over time" in query_lower:
        metric_keywords = {
            "congestion": "congestion_index", "aqi": "AQI_mean", "speed": "SPEED",
            "temperature": "tavg", "precipitation": "prcp", "wind speed": "wspd",
            "public transport trips": "TOTAL PUBLIC TRANSPORT TRIP", "traffic volume": "TRAFFIC_VOLUME"
        }
        selected_metric_col = None
        for keyword, col_name in metric_keywords.items():
            if keyword in query_lower:
                selected_metric_col = col_name
                break

        if not selected_metric_col:
            return "Please specify which metric's trend you want to see (e.g., congestion, AQI, speed).", None

        if selected_metric_col not in data_frame.columns:
            return f"The '{selected_metric_col}' column is not available in the dataset.", None

        city_specified = False
        for city in data_frame['CITY'].unique():
            if city.lower() in query_lower:
                city_specified = True
                city_data = data_frame[data_frame['CITY'].str.lower() == city.lower()].copy()
                if city_data.empty:
                    return f"No data for {city} with current filters to plot trend for {selected_metric_col}.", None
                if 'date' not in city_data.columns or not pd.api.types.is_datetime64_any_dtype(city_data['date']):
                    st.warning(f"Date column not found or not in datetime format for {city}. Cannot plot trend.")
                    return f"Could not plot trend for {city} due to date column issues.", None

                city_data = city_data.sort_values(by='date')
                px_fig = px.line(city_data, x='date', y=selected_metric_col, 
                                 title=f"{selected_metric_col.replace('_', ' ').title()} Trend in {city}",
                                 labels={'date': 'Date', selected_metric_col: selected_metric_col.replace('_', ' ').title()},
                                 template=plot_template,
                                 color_discrete_sequence=["#00D4FF"], # Vibrant blue
                                 height=default_plot_height)
                px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
                st.plotly_chart(px_fig, use_container_width=True)
                plot_generated = True
                return f"Interactive trend of {selected_metric_col.replace('_', ' ')} in {city}.", None

        # If no specific city, plot overall trend
        if not city_specified:
            if 'date' not in data_frame.columns or not pd.api.types.is_datetime64_any_dtype(data_frame['date']):
                st.warning(f"Date column not found or not in datetime format. Cannot plot overall trend.")
                return f"Could not plot overall trend due to date column issues.", None

            overall_trend_data = data_frame.groupby('date')[selected_metric_col].mean().reset_index()
            overall_trend_data = overall_trend_data.sort_values(by='date')

            px_fig = px.line(overall_trend_data, x='date', y=selected_metric_col, 
                             title=f"Overall {selected_metric_col.replace('_', ' ').title()} Trend Across All Cities",
                             labels={'date': 'Date', selected_metric_col: selected_metric_col.replace('_', ' ').title()},
                             template=plot_template,
                             color_discrete_sequence=["#7C4DFF"], # More dim purple accent
                             height=default_plot_height)
            px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
            st.plotly_chart(px_fig, use_container_width=True)
            plot_generated = True
            return f"Interactive overall trend of {selected_metric_col.replace('_', ' ')} across all cities.", None

    # 2. Scatter Plots (Plotly)
    elif "scatter" in query_lower or "relationship" in query_lower or ("vs" in query_lower and any(col in query_lower for col in ['congestion', 'temperature', 'precipitation', 'wind', 'population', 'aqi', 'public transport', 'speed', 'volume'])):
        all_numeric_cols = data_frame.select_dtypes(include='number').columns.tolist()
        col_map = {
            "congestion": "congestion_index", "aqi": "AQI_mean", "speed": "SPEED",
            "temperature": "tavg", "precipitation": "prcp", "wind speed": "wspd", "wind": "wspd",
            "public transport trips": "TOTAL PUBLIC TRANSPORT TRIP", "public transport": "TOTAL PUBLIC TRANSPORT TRIP",
            "population density": "POPULATION DENSITY", "population": "POPULATION DENSITY",
            "traffic volume": "TRAFFIC_VOLUME", "volume": "TRAFFIC_VOLUME"
        }

        found_cols = []
        for term, col_name in col_map.items():
            if term in query_lower and col_name in all_numeric_cols:
                found_cols.append(col_name)

        potential_x, potential_y = None, None
        if len(found_cols) >= 2:
            if "congestion_index" in found_cols:
                potential_y = "congestion_index"
                found_cols.remove("congestion_index")
                potential_x = found_cols[0]
            else:
                potential_x, potential_y = found_cols[0], found_cols[1]
        elif len(found_cols) == 1:
            return f"Please specify two numeric columns for a scatter plot. You mentioned '{found_cols[0].replace('_', ' ')}'.", None
        else:
            return "Please specify two numeric columns for the scatter plot, e.g., 'AQI and congestion' or 'speed and volume'.", None

        if potential_x and potential_y:
            if potential_x not in data_frame.columns or potential_y not in data_frame.columns:
                return f"One or both of the specified columns ('{potential_x}', '{potential_y}') are not available.", None

            plot_data = data_frame.dropna(subset=[potential_x, potential_y])
            if plot_data.empty:
                return f"No valid data points for a scatter plot of '{potential_x.replace('_', ' ')}' vs '{potential_y.replace('_', ' ')}' after filtering NaN values.", None

            city_specified_in_query = False
            selected_city_for_plot = None
            for city_name in data_frame['CITY'].unique():
                if city_name.lower() in query_lower:
                    city_specified_in_query = True
                    selected_city_for_plot = city_name
                    break

            if city_specified_in_query:
                city_data = plot_data[plot_data['CITY'].str.lower() == selected_city_for_plot.lower()]
                if city_data.empty:
                    return f"No data for {selected_city_for_plot} with current filters to plot {potential_x.replace('_', ' ')} vs {potential_y.replace('_', ' ')}.", None

                px_fig = px.scatter(city_data, x=potential_x, y=potential_y, 
                                    title=f"{potential_y.replace('_', ' ').title()} vs {potential_x.replace('_', ' ').title()} in {selected_city_for_plot}",
                                    labels={potential_x: potential_x.replace('_', ' ').title(), potential_y: potential_y.replace('_', ' ').title()},
                                    template=plot_template,
                                    color_discrete_sequence=["#FFA726"], # Vibrant orange accent
                                    height=default_plot_height)
                px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
                st.plotly_chart(px_fig, use_container_width=True)
                plot_generated = True
                return f"Interactive scatter plot showing {potential_y.replace('_', ' ')} vs. {potential_x.replace('_', ' ')} in {selected_city_for_plot}.", None
            else:
                px_fig = px.scatter(data_frame=plot_data, x=potential_x, y=potential_y, 
                                    color='CITY' if data_frame['CITY'].nunique() > 1 else None,
                                    title=f"{potential_y.replace('_', ' ').title()} vs {potential_x.replace('_', ' ').title()} Across Cities",
                                    labels={potential_x: potential_x.replace('_', ' ').title(), potential_y: potential_y.replace('_', ' ').title()},
                                    template=plot_template,
                                    color_discrete_sequence=px.colors.qualitative.Plotly, # Use a good default palette
                                    height=default_plot_height
                                    )
                px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
                st.plotly_chart(px_fig, use_container_width=True)
                plot_generated = True
                return f"Interactive scatter plot showing {potential_y.replace('_', ' ')} vs. {potential_x.replace('_', ' ')} across all filtered cities.", None
        else:
            return "Could not determine appropriate columns for scatter plot. Please be more specific.", None

    # 3. Boxplot (by categorical) (Plotly)
    elif ("boxplot" in query_lower or "distribution" in query_lower) and "by" in query_lower:
        parts = query_lower.split(" by ")
        if len(parts) == 2:
            value_col_raw = parts[0].replace("show", "").replace("distribution", "").strip()
            category_col_raw = parts[1].replace("type", "").strip()

            col_map = {
                "speed": "SPEED", "congestion": "congestion_index", "aqi": "AQI_mean",
                "temperature": "tavg", "precipitation": "prcp", "management": "MANAGEMENT_TYPE",
                "management type": "MANAGEMENT_TYPE", "city": "CITY"
            }
            value_col = col_map.get(value_col_raw, None)
            category_col = col_map.get(category_col_raw, None)

            if value_col and category_col:
                if value_col not in data_frame.columns or category_col not in data_frame.columns:
                    return f"One or both of the specified columns ('{value_col}', '{category_col}') are not available for boxplot.", None

                plot_data = data_frame.dropna(subset=[value_col, category_col])
                if plot_data.empty or plot_data[category_col].nunique() < 2:
                    return f"Not enough valid data or unique categories in '{category_col}' to create a boxplot for '{value_col}'.", None

                px_fig = px.box(plot_data, x=category_col, y=value_col, 
                                title=f"{value_col.replace('_', ' ').title()} Distribution by {category_col.replace('_', ' ').title()}",
                                labels={category_col: category_col.replace('_', ' ').title(), value_col: value_col.replace('_', ' ').title()},
                                template=plot_template,
                                color=category_col if plot_data[category_col].nunique() < 10 else None, # Color by category if not too many
                                color_discrete_sequence=px.colors.qualitative.D3, # Good qualitative palette
                                height=default_plot_height
                                )
                px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
                st.plotly_chart(px_fig, use_container_width=True)
                plot_generated = True
                return f"Interactive boxplot of {value_col.replace('_', ' ')} distribution by {category_col.replace('_', ' ')}.", None
            else:
                return "Could not determine columns for boxplot. Please specify a numeric column and a categorical column, e.g., 'speed by management type'.", None

    # 4. Ranking (Plotly Bar Chart with Dynamic Height)
    elif "rank" in query_lower:
        metric_keywords = {
            "congestion": "congestion_index", "aqi": "AQI_mean", "speed": "SPEED",
            "temperature": "tavg", "precipitation": "prcp", "wind speed": "wspd",
            "public transport trips": "TOTAL PUBLIC TRANSPORT TRIP", "population density": "POPULATION DENSITY",
            "traffic volume": "TRAFFIC_VOLUME"
        }
        selected_metric_col = None
        for keyword, col_name in metric_keywords.items():
            if keyword in query_lower:
                selected_metric_col = col_name
                break

        if not selected_metric_col:
            return "Please specify which metric you want to rank cities by (e.g., congestion, AQI, speed).", None

        if selected_metric_col not in data_frame.columns:
            return f"The '{selected_metric_col}' column is not available in the dataset for ranking.", None

        ascending_rank = True
        if selected_metric_col in ["congestion_index", "AQI_mean"] or "worst" in query_lower or "highest" in query_lower:
            ascending_rank = False
        if "best" in query_lower or "lowest" in query_lower:
            ascending_rank = True

        avg_metric = data_frame.groupby("CITY")[selected_metric_col].mean().sort_values(ascending=ascending_rank).reset_index()

        if avg_metric.empty:
            return f"Not enough data to rank cities by {selected_metric_col.replace('_', ' ')} with current filters.", None

        # DYNAMIC SIZING: Calculate height based on number of cities (2x original)
        num_cities = len(avg_metric['CITY'])
        plot_height = max(600, num_cities * 70)  # Base height 600, add 70px per city

        rank_order = "lowest" if ascending_rank else "highest"
        
        px_fig = px.bar(avg_metric, x=selected_metric_col, y='CITY', orientation='h',
                        title=f"Average {selected_metric_col.replace('_', ' ').title()} by City",
                        labels={selected_metric_col: f"Average {selected_metric_col.replace('_', ' ').title()}", 'CITY': 'City'},
                        template=plot_template,
                        color=selected_metric_col,
                        color_continuous_scale=px.colors.sequential.Plasma,
                        height=plot_height # Set dynamic height
                        )
        px_fig.update_layout(yaxis={'categoryorder':'total ascending' if ascending_rank else 'total descending'})
        px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
        st.plotly_chart(px_fig, use_container_width=True)
        plot_generated = True
        return f"Interactive ranking of cities by average {selected_metric_col.replace('_', ' ')}. {rank_order.capitalize()} values are {'better' if ascending_rank else 'worse'}.", None

    # 5. Impact by factor (Plotly Bar Chart)
    elif "most affected by" in query_lower or "impact of" in query_lower:
        feature_map = {
            "precipitation": "prcp", "aqi": "AQI_mean", "wind": "wspd",
            "temperature": "tavg", "population density": "POPULATION DENSITY",
            "public transport trips": "TOTAL PUBLIC TRANSPORT TRIP"
        }
        target_col = "congestion_index"
        if "on" in query_lower:
            parts = query_lower.split(" on ")
            if len(parts) == 2:
                target_keyword = parts[1].strip()
                if "speed" in target_keyword:
                    target_col = "SPEED"
                elif "traffic volume" in target_keyword:
                    target_col = "TRAFFIC_VOLUME"

        selected_factor_col = None
        for keyword, col_name in feature_map.items():
            if keyword in query_lower:
                selected_factor_col = col_name
                break

        if not selected_factor_col:
            return "Please specify a factor to analyze its impact (e.g., precipitation, temperature, AQI).", None

        if selected_factor_col not in data_frame.columns or target_col not in data_frame.columns:
            return f"Required column '{selected_factor_col}' or '{target_col}' not found for impact analysis.", None

        corrs = []
        cities_for_corr = []
        for city_name in data_frame['CITY'].unique():
            city_df = data_frame[data_frame['CITY'] == city_name]
            if len(city_df.dropna(subset=[selected_factor_col, target_col])) > 1 and \
               city_df[selected_factor_col].nunique() > 1 and city_df[target_col].nunique() > 1:
                corr_val = city_df[selected_factor_col].corr(city_df[target_col])
                if pd.notnull(corr_val):
                    corrs.append({"CITY": city_name, "Absolute Correlation": abs(corr_val), "Correlation": corr_val})
                    cities_for_corr.append(city_name) # Ensure city is added to list

        if not corrs:
             return f"Could not calculate correlations for {selected_factor_col} impact on {target_col} with current filters; insufficient data or too many missing values.", None

        corr_df = pd.DataFrame(corrs).sort_values(by="Absolute Correlation", ascending=False)
        
        px_fig = px.bar(corr_df, x="Absolute Correlation", y="CITY", orientation='h',
                        title=f"Cities by Impact of {selected_factor_col.replace('_', ' ').title()} on {target_col.replace('_', ' ').title()} (Absolute Correlation)",
                        labels={"Absolute Correlation": f"Absolute Correlation with {target_col.replace('_', ' ').title()} Index", "CITY": "City"},
                        template=plot_template,
                        color="Absolute Correlation", color_continuous_scale=px.colors.sequential.Plasma, # New palette for dark theme
                        height=default_plot_height
                        )
        px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
        st.plotly_chart(px_fig, use_container_width=True)
        plot_generated = True
        return f"Interactive rank of cities by absolute correlation between {selected_factor_col.replace('_', ' ')} and {target_col.replace('_', ' ')}.", None

    # 6. Compare two cities (Plotly Bar Chart)
    elif "compare" in query_lower and "and" in query_lower:
        cities_in_query = []
        query_words = query_lower.replace(',', ' ').replace(' and ', ' ').split()
        unique_df_cities_lower = {c.lower(): c for c in data_frame["CITY"].unique()}

        for word in query_words:
            if word.lower() in unique_df_cities_lower:
                cities_in_query.append(unique_df_cities_lower[word.lower()])

        if len(cities_in_query) == 2:
            metric_keywords = {
                "congestion": "congestion_index", "aqi": "AQI_mean", "speed": "SPEED",
                "temperature": "tavg", "precipitation": "prcp", "wind speed": "wspd",
                "public transport trips": "TOTAL PUBLIC TRANSPORT TRIP", "population density": "POPULATION DENSITY",
                "traffic volume": "TRAFFIC_VOLUME"
            }
            selected_metric_col = "congestion_index"
            for keyword, col_name in metric_keywords.items():
                if keyword in query_lower:
                    selected_metric_col = col_name
                    break

            if selected_metric_col not in data_frame.columns:
                return f"The '{selected_metric_col}' column is not available for comparison.", None

            cities_to_compare = cities_in_query
            subset = data_frame[data_frame["CITY"].isin(cities_to_compare)]
            if subset.empty:
                return f"No data for {cities_to_compare[0]} and {cities_to_compare[1]} with current filters.", None

            avg_metric_df = subset.groupby("CITY")[selected_metric_col].mean().reset_index()
            avg_metric_df = avg_metric_df[avg_metric_df['CITY'].isin(cities_to_compare)] # Filter to ensure only queried cities

            if len(avg_metric_df) < 2:
                return f"Could not find sufficient {selected_metric_col.replace('_', ' ')} data for both specified cities with current filters.", None

            px_fig = px.bar(avg_metric_df, x='CITY', y=selected_metric_col, 
                            title=f"Average {selected_metric_col.replace('_', ' ').title()}: {cities_to_compare[0]} vs {cities_to_compare[1]}",
                            labels={'CITY': 'City', selected_metric_col: f"Average {selected_metric_col.replace('_', ' ').title()}"},
                            template=plot_template,
                            color='CITY', # Color bars by city
                            color_discrete_map={cities_to_compare[0]: "#00D4FF", cities_to_compare[1]: "#7C4DFF"}, # Custom colors
                            height=default_plot_height
                            )
            px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
            st.plotly_chart(px_fig, use_container_width=True)
            plot_generated = True
            return f"Interactive comparison of average {selected_metric_col.replace('_', ' ')} between {cities_to_compare[0]} and {cities_to_compare[1]}.", None
        else:
            return "Please specify exactly two cities to compare.", None

    # 7. Speed comparison by management type (Plotly Boxplot)
    elif ("speed" in query_lower and ("ai" in query_lower or "conventional" in query_lower or "management" in query_lower)):
        if 'MANAGEMENT_TYPE' not in data_frame.columns or 'SPEED' not in data_frame.columns:
            return "Required columns (MANAGEMENT_TYPE, SPEED) are missing for this plot.", None

        plot_data = data_frame.dropna(subset=['MANAGEMENT_TYPE', 'SPEED'])
        if plot_data.empty or plot_data['MANAGEMENT_TYPE'].nunique() < 2:
            return "Not enough unique management types or speed data to create a boxplot with current filters.", None

        px_fig = px.box(plot_data, x="MANAGEMENT_TYPE", y="SPEED", 
                        title="Traffic Speed: AI vs Conventional Management",
                        labels={"MANAGEMENT_TYPE": "Management Type", "SPEED": "Speed"},
                        template=plot_template,
                        color="MANAGEMENT_TYPE", # Color by management type
                        color_discrete_map={"AI": "#00D4FF", "Conventional": "#7C4DFF"}, # Custom palette
                        height=default_plot_height
                        )
        px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
        st.plotly_chart(px_fig, use_container_width=True)
        plot_generated = True
        return "Interactive boxplot comparing traffic speed distributions between AI and conventionally managed systems.", None

    # 8. Correlation between two numeric columns (Text output, no plot)
    elif ("correlated" in query_lower or "correlation" in query_lower) and "with" in query_lower:
        parts = query_lower.split(" with ")
        if len(parts) == 2:
            col1_raw = parts[0].replace("what is the correlation between", "").strip()
            col2_raw = parts[1].strip()

            col_map = {
                "wind speed": "wspd", "wind": "wspd", "congestion": "congestion_index",
                "aqi": "AQI_mean", "temperature": "tavg", "precipitation": "prcp",
                "population density": "POPULATION DENSITY", "public transport trips": "TOTAL PUBLIC TRANSPORT TRIP",
                "traffic volume": "TRAFFIC_VOLUME", "speed": "SPEED"
            }
            col1 = col_map.get(col1_raw, None)
            col2 = col_map.get(col2_raw, None)

            if col1 and col2:
                if col1 not in data_frame.columns or col2 not in data_frame.columns:
                    return f"One or both of the specified columns ('{col1}', '{col2}') are not available for correlation.", None

                city_found = False
                for city in data_frame["CITY"].unique():
                    if city.lower() in query_lower:
                        city_found = True
                        subset = data_frame[data_frame["CITY"].str.lower() == city.lower()]
                        if subset.empty:
                            return f"No data for {city} with current filters to calculate correlation between {col1} and {col2}.", None

                        subset_clean = subset.dropna(subset=[col1, col2])
                        if len(subset_clean) < 2 or subset_clean[col1].nunique() < 2 or subset_clean[col2].nunique() < 2:
                            return f"Not enough varying data to calculate correlation between {col1} and {col2} for {city} with current filters.", None

                        correlation = subset_clean[col1].corr(subset_clean[col2])
                        if pd.isna(correlation):
                            return f"Could not calculate correlation for {city} (likely due to insufficient or non-varying data with current filters).", None
                        return f"The correlation between {col1.replace('_', ' ')} and {col2.replace('_', ' ')} in {city} is **{correlation:.2f}**.", None

                if not city_found:
                    subset_clean = data_frame.dropna(subset=[col1, col2])
                    if len(subset_clean) < 2 or subset_clean[col1].nunique() < 2 or subset_clean[col2].nunique() < 2:
                        return f"Not enough varying data to calculate overall correlation between {col1} and {col2} with current filters.", None

                    correlation = subset_clean[col1].corr(subset_clean[col2])
                    if pd.isna(correlation):
                        return f"Could not calculate overall correlation (likely due to insufficient or non-varying data with current filters).", None
                    return f"The overall correlation between {col1.replace('_', ' ')} and {col2.replace('_', ' ')} across all filtered data is **{correlation:.2f}**.", None
            else:
                return "Please specify two valid numeric columns for correlation (e.g., 'wind speed and congestion').", None
        else:
            return "Please rephrase your correlation query using 'X with Y' format.", None

    # 9. Temperature impact on congestion (Plotly Bar Chart)
    elif ("temperature" in query_lower and ("effect" in query_lower or "impact" in query_lower) and "congestion" in query_lower):
        val_col = "tavg"
        target_col = "congestion_index"
        if val_col not in data_frame.columns or target_col not in data_frame.columns:
            return f"Required columns ('{val_col}', '{target_col}') not found for temperature impact analysis.", None

        corrs = []
        for city_name in data_frame['CITY'].unique():
            city_df = data_frame[data_frame['CITY'] == city_name]
            if len(city_df.dropna(subset=[val_col, target_col])) > 1 and \
               city_df[val_col].nunique() > 1 and city_df[target_col].nunique() > 1:
                corr_val = city_df[val_col].corr(city_df[target_col])
                if pd.notnull(corr_val):
                    corrs.append({"CITY": city_name, "Absolute Correlation": abs(corr_val), "Correlation": corr_val})

        if not corrs:
            return "Could not calculate temperature impact correlations with current filters; insufficient data.", None

        corr_df = pd.DataFrame(corrs).sort_values(by="Absolute Correlation", ascending=False)
        
        px_fig = px.bar(corr_df, x="Absolute Correlation", y="CITY", orientation='h',
                        title="Cities by Impact of Temperature on Congestion (Absolute Correlation)",
                        labels={"Absolute Correlation": "Absolute Correlation with Congestion Index", "CITY": "City"},
                        template=plot_template,
                        color="Absolute Correlation", color_continuous_scale=px.colors.sequential.OrRd, # Changed palette for dark theme
                        height=default_plot_height
                        )
        px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
        st.plotly_chart(px_fig, use_container_width=True)
        plot_generated = True
        return f"{corr_df['CITY'].iloc[0]} shows the highest absolute correlation between temperature and congestion. This plot shows the strength of this relationship across cities.", None

    # 10. Strongest factor affecting congestion (Plotly Bar Chart)
    elif "strongest factor" in query_lower or ("strongest" in query_lower and "effect" in query_lower):
        target_col = "congestion_index"
        if "on speed" in query_lower:
            target_col = "SPEED"
        elif "on traffic volume" in query_lower:
            target_col = "TRAFFIC_VOLUME"

        possible_factors = ["AQI_mean", "prcp", "tavg", "wspd", "POPULATION DENSITY", "TOTAL PUBLIC TRANSPORT TRIP", "TRAFFIC_VOLUME", "SPEED"]
        numeric_cols_present = [col for col in possible_factors if col in data_frame.columns and
                                pd.api.types.is_numeric_dtype(data_frame[col]) and col != target_col]

        if not numeric_cols_present:
            return "No suitable numeric factor columns found to analyze the strongest effect with current filters.", None
        if target_col not in data_frame.columns or not pd.api.types.is_numeric_dtype(data_frame[target_col]):
            return f"{target_col.replace('_', ' ')} column is missing or not numeric, cannot perform correlation analysis.", None

        corr_values = {}
        for col in numeric_cols_present:
            subset_clean = data_frame.dropna(subset=[col, target_col])
            if len(subset_clean) > 1 and subset_clean[col].nunique() > 1 and subset_clean[target_col].nunique() > 1:
                correlation = subset_clean[col].corr(subset_clean[target_col])
                if pd.notnull(correlation):
                    corr_values[col] = correlation

        if not corr_values:
            return f"Could not calculate correlations for any factors with current filters (likely due to insufficient or non-varying data for {target_col.replace('_', ' ')}).", None

        corr_df = pd.DataFrame(list(corr_values.items()), columns=['Factor', 'Correlation'])
        corr_df['Absolute Correlation'] = corr_df['Correlation'].abs()
        corr_df = corr_df.sort_values(by='Absolute Correlation', ascending=False)

        px_fig = px.bar(corr_df, x="Correlation", y="Factor", orientation='h',
                        title=f"Correlation of Various Factors with {target_col.replace('_', ' ').title()}",
                        labels={"Correlation": "Correlation Coefficient (closer to +/-1 indicates stronger relationship)", "Factor": "Factor"},
                        template=plot_template,
                        color="Correlation", color_continuous_scale=px.colors.sequential.RdPu, # New palette for dark theme
                        height=default_plot_height
                        )
        px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
        st.plotly_chart(px_fig, use_container_width=True)
        plot_generated = True
        return f"The factor with the strongest absolute correlation to {target_col.replace('_', ' ')} is **{corr_df['Factor'].iloc[0].replace('_', ' ')}** (Correlation: {corr_df['Correlation'].iloc[0]:.2f}). The plot shows other factors as well.", None

    # 11. Correlation Heatmap (Plotly with Dynamic Height)
    elif "heatmap" in query_lower or "correlation matrix" in query_lower:
        numeric_df = data_frame.select_dtypes(include='number')
        if numeric_df.shape[1] < 2:
             return "Not enough numeric data to generate a correlation heatmap with current filters.", None

        numeric_df_cleaned = numeric_df.dropna(axis=1, how='all')
        if numeric_df_cleaned.shape[1] < 2:
            return "Not enough numeric columns with valid data to generate a correlation heatmap.", None

        corr_matrix = numeric_df_cleaned.corr()
        if corr_matrix.empty:
            return "Could not compute correlation matrix; likely no variance in filtered numeric data.", None

        # DYNAMIC SIZING: Calculate height based on number of features (2x original)
        num_features = len(corr_matrix.columns)
        plot_height = max(800, num_features * 60) # Base height 800, add 60px per feature

        px_fig = px.imshow(corr_matrix, 
                           text_auto=".2f", # Show correlation values on heatmap, formatted to 2 decimal places
                           color_continuous_scale=px.colors.sequential.Magma if plot_template == "plotly_dark" else px.colors.sequential.Blues,
                           aspect="equal", # Make it a square grid
                           title="Correlation Heatmap of Numeric Features",
                           template=plot_template,
                           height=plot_height # Set dynamic height
                           )
        px_fig.update_xaxes(side="bottom") # Ensure x-axis labels are at the bottom
        px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
        px_fig.update_traces(textfont_size=16) # Increased font size for values on heatmap
        st.plotly_chart(px_fig, use_container_width=True) # use_container_width will respect the width, and the height is set in layout
        plot_generated = True
        return "Interactive correlation heatmap showing relationships between all numeric features in the dataset. The plot size has been adjusted for better visibility.", None

    # 12. Multivariable AQI vs Volume by Management/City (Plotly Scatter)
    elif ("volume" in query_lower or "traffic volume" in query_lower) and ("aqi" in query_lower or "congestion" in query_lower) and ("by management" in query_lower or "by city" in query_lower):
        x_col, y_col, hue_col = None, None, None

        if "aqi" in query_lower: x_col = "AQI_mean"
        elif "congestion" in query_lower: x_col = "congestion_index"

        if "volume" in query_lower or "traffic volume" in query_lower: y_col = "TRAFFIC_VOLUME"
        elif "speed" in query_lower: y_col = "SPEED"

        if "by management" in query_lower: hue_col = "MANAGEMENT_TYPE"
        elif "by city" in query_lower: hue_col = "CITY"
        else: return "Please specify grouping for scatter plot (e.g., 'by management' or 'by city').", None

        if not all(c in data_frame.columns for c in [x_col, y_col, hue_col]):
            return f"One or more required columns ({x_col}, {y_col}, {hue_col}) are missing for this plot with current filters.", None

        plot_data = data_frame.dropna(subset=[x_col, y_col, hue_col])
        if plot_data.empty or plot_data[hue_col].nunique() < 2:
            return f"Insufficient data or unique '{hue_col.replace('_', ' ')}' values for scatter plot with current filters.", None

        px_fig = px.scatter(plot_data, x=x_col, y=y_col, color=hue_col, 
                            title=f"{y_col.replace('_', ' ').title()} vs {x_col.replace('_', ' ').title()}, by {hue_col.replace('_', ' ').title()}",
                            labels={x_col: x_col.replace('_', ' ').title(), y_col: y_col.replace('_', ' ').title(), hue_col: hue_col.replace('_', ' ').title()},
                            template=plot_template,
                            color_discrete_sequence=px.colors.qualitative.Vivid if plot_template == "plotly_dark" else px.colors.qualitative.Safe, # Varied palette
                            height=default_plot_height
                            )
        px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
        st.plotly_chart(px_fig, use_container_width=True)
        plot_generated = True
        return f"Interactive scatter plot showing {y_col.replace('_', ' ')} vs. {x_col.replace('_', ' ')}, color-coded by {hue_col.replace('_', ' ')}.", None

    # 13. Season-based analysis (Plotly Boxplot)
    elif "season" in query_lower or "seasonal" in query_lower:
        if 'date' not in data_frame.columns or not pd.api.types.is_datetime64_any_dtype(data_frame['date']):
            return "Date column not found or not in datetime format. Cannot analyze by season.", None

        def get_season(date):
            month = date.month
            if 3 <= month <= 5: return 'Spring'
            elif 6 <= month <= 8: return 'Summer'
            elif 9 <= month <= 11: return 'Autumn'
            else: return 'Winter'

        temp_df = data_frame.copy()
        temp_df['season'] = temp_df['date'].apply(get_season)

        if "congestion by season" in query_lower or "seasonal congestion" in query_lower or "congestion in seasons" in query_lower:
            if 'congestion_index' not in temp_df.columns:
                return "Congestion index column not found for seasonal analysis.", None

            plot_data = temp_df.dropna(subset=['congestion_index', 'season'])
            if plot_data.empty:
                return "No valid data to plot seasonal congestion after filtering NaN values.", None

            px_fig = px.box(plot_data, x='season', y='congestion_index', 
                            category_orders={"season": ['Spring', 'Summer', 'Autumn', 'Winter']},
                            title="Congestion Index Distribution by Season",
                            labels={'season': 'Season', 'congestion_index': 'Congestion Index'},
                            template=plot_template,
                            color='season', # Color by season
                            color_discrete_sequence=px.colors.qualitative.Pastel, # Changed palette for dark theme
                            height=default_plot_height
                            )
            px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
            st.plotly_chart(px_fig, use_container_width=True)
            plot_generated = True
            return "Interactive boxplot showing congestion index distribution by season.", None

        return "Please specify what seasonal analysis you'd like (e.g., 'congestion by season').", None

    # 14. Holiday vs Non-Holiday analysis (Plotly Boxplot)
    elif "holiday" in query_lower:
        if 'Holiday_Flag' not in data_frame.columns:
            return "The 'Holiday_Flag' column is not found in the dataset. Please ensure your 'city_data.csv' includes this column with boolean (True/False) values to analyze holiday impact.", None
        if 'congestion_index' not in data_frame.columns:
            return "Congestion index column not found for holiday analysis.", None

        plot_data = data_frame.dropna(subset=['congestion_index', 'Holiday_Flag'])
        if plot_data.empty or plot_data['Holiday_Flag'].nunique() < 2:
            return "Not enough valid data or unique values in 'Holiday_Flag' to compare holiday vs non-holiday congestion. Ensure there are both holiday and non-holiday entries.", None

        px_fig = px.box(plot_data, x='Holiday_Flag', y='congestion_index', 
                        title="Congestion Index: Holiday vs Non-Holiday",
                        labels={'Holiday_Flag': 'Is Holiday?', 'congestion_index': 'Congestion Index'},
                        template=plot_template,
                        color='Holiday_Flag', # Color by holiday flag
                        color_discrete_map={True: "#00D4FF", False: "#7C4DFF"}, # Custom palette
                        height=default_plot_height
                        )
        px_fig.update_xaxes(tickvals=[0, 1], ticktext=['Non-Holiday', 'Holiday'])
        px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
        st.plotly_chart(px_fig, use_container_width=True)
        plot_generated = True
        return "Interactive boxplot comparing congestion index on holidays versus non-holidays.", None

    # Default fallback
    return "I'm still learning to understand this question. Try asking for trends, comparisons, rankings, correlations, or specific plots like heatmaps. Be more specific about columns.", None

# =============================================================================
#                     GEMINI LLM INTEGRATION (UNCHANGED)
# =============================================================================
def get_gemini_answer(query, context_summary, plot_description):
    """
    Integrates with the Gemini LLM to provide explanations and insights
    based on the user's query and the analysis results.
    """
    if not gemini_api_key:
        return "Gemini LLM not active. Please enter your Gemini API key in the sidebar to get AI-powered explanations."
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        prompt_parts = [
            "You are an expert traffic analyst and data interpreter. Your goal is to provide concise, insightful explanations based on user queries and provided data context.",
            f"User Question: {query}",
            f"Dataset Summary (overall statistics and filters applied):\n{context_summary}"
        ]
        if plot_description and "I'm still learning" not in plot_description:
            prompt_parts.append(f"System description of generated visual: '{plot_description}'. Please elaborate and interpret the visual if one was generated. Focus on key insights from the plot.")
        else:
            prompt_parts.append("No specific plot was generated by the system. Base your response on the dataset context and potential insights from the data itself. Suggest what kind of plot would be useful.")
        
        prompt = "\n\n".join(prompt_parts)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini error: {e}")
        return "Could not retrieve a response from Gemini. Check your API key and ensure it's correctly entered."

# =============================================================================
#                                RUN QUERY
# =============================================================================
if user_query:
    # Wrap analysis result section in a container
    with st.container(border=True):
        st.markdown('<hr class="main-separator" />', unsafe_allow_html=True)
        with st.spinner("Analyzing your query..."):
            # Pass the selected Plotly template to the plotting function
            response_text, fig_object = plot_and_answer(user_query, df, plotly_template)

            st.subheader("Analysis Result")
            st.write(response_text)

            # Only provide download button for Matplotlib figures (Plotly figures have built-in download)
            if fig_object: # This means a Matplotlib figure was returned (e.g., if a new plot type is added later)
                buf = io.BytesIO()
                fig_object.savefig(buf, format="png", bbox_inches='tight', facecolor=fig_object.get_facecolor())
                buf.seek(0)
                st.download_button("Download Plot (PNG)", buf, "plot.png", "image/png")
                plt.close(fig_object)
            elif "Interactive" in response_text: # If a Plotly figure was generated
                 st.info("The interactive plot above allows zooming, panning, and data inspection. You can download it directly from the plot's menu.")

            if gemini_api_key:
                st.subheader("Gemini-enhanced Explanation")
                context = ""
                if df is not None and not df.empty:
                    numeric_cols = df.select_dtypes(include='number').columns.tolist()
                    non_numeric_cols = df.select_dtypes(exclude='number').columns.tolist()
                    context = f"Numerical features in filtered data: {', '.join(numeric_cols)}.\nCategorical features in filtered data: {', '.join(non_numeric_cols)}.\nNumber of rows in filtered data: {len(df)}.\nUnique Cities in filtered data: {df['CITY'].nunique()}."
                    if 'date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['date']):
                        context += f"\nDate Range in filtered data: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}."
                    if 'Holiday_Flag' in df.columns:
                        holiday_count = df['Holiday_Flag'].sum()
                        non_holiday_count = len(df) - holiday_count
                        context += f"\nHoliday entries: {holiday_count}, Non-holiday entries: {non_holiday_count}."
                else:
                    context = "No data loaded or available after filters. Gemini will provide a general explanation."

                gemini_response = get_gemini_answer(user_query, context, response_text)
                st.markdown(gemini_response)
            elif not fig_object and "I'm still learning" in response_text and 'plot_generated' not in locals():
                st.info("Try asking about trends, comparisons, or add a Gemini key for enhanced insights.")
# -------------------- Separator before “Download Filtered Data” --------------------
st.markdown('<hr class="main-separator" />', unsafe_allow_html=True)

# =============================================================================
#                       DATA DOWNLOAD (UNCHANGED)
# =============================================================================
# Wrap data download section in a container
with st.container(border=True):
    st.header("Download Filtered Data")
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv_data,
        file_name="filtered_traffic_data.csv",
        mime="text/csv",
    )
    st.info("This download provides the data currently visible/used after applying all filters.")

# -------------------- Separator before “City Traffic Dashboard” --------------------
st.markdown('<hr class="main-separator" />', unsafe_allow_html=True)

# =============================================================================
#                           CITY DASHBOARD PANEL
# =============================================================================
# Wrap city dashboard section in a container
with st.container(border=True):
    st.header("City Traffic Dashboard")
    city_geojsons = {
        "BARCELONA": "geojson/barcelona_congestion_randomized.geojson",
        "LONDON": "geojson/london_congestion_randomized.geojson",
        "NEW YORK CITY": "geojson/new_york_congestion_randomized.geojson",
        "LOS ANGELES": "geojson/los_angeles_congestion_randomized.geojson",
        "PARIS": "geojson/paris_congestion_randomized.geojson",
        "MELBOURNE": "geojson/melbourne_congestion_randomized.geojson",
        "BANGALORE": "geojson/bangalore_congestion_randomized.geojson",
        "BUENOS AIRES": "geojson/buenos_aires_congestion_randomized.geojson"
    }

    st.sidebar.subheader("City Dashboard Controls")
    dashboard_city = st.sidebar.selectbox("Select a City for Dashboard", list(city_geojsons.keys()))

    @st.cache_data
    def load_single_geojson(geo_path):
        """
        Loads a single GeoJSON file using geopandas.
        Caches the result for performance.
        """
        try:
            return gpd.read_file(geo_path)
        except Exception as e:
            st.error(f"Error loading GeoJSON file '{geo_path}': {e}. Please check file path and content.")
            return None

    geo_path = city_geojsons.get(dashboard_city)
    gdf = None
    if geo_path:
        gdf = load_single_geojson(geo_path)


    if gdf is None:
        st.warning(f"GeoJSON data could not be loaded for {dashboard_city}. Map controls are disabled.")


    if 'date' in df_original.columns and pd.api.types.is_datetime64_any_dtype(df_original['date']):
        available_dates_for_dashboard_city = df_original[df_original['CITY'] == dashboard_city]['date'].unique()
        # Check if available_dates_for_dashboard_city is not empty before accessing .size
        if available_dates_for_dashboard_city.size > 0: 
            min_date_dash = pd.to_datetime(available_dates_for_dashboard_city.min())
            max_date_dash = pd.to_datetime(available_dates_for_dashboard_city.max())
            default_date_dash = max_date_dash
            dashboard_date_selected = st.sidebar.date_input(
                "Select Date for Dashboard Stats",
                default_date_dash,
                min_value=min_date_dash,
                max_value=max_date_dash
            )
        else:
            st.warning(f"No date data available for {dashboard_city} in the original dataset.")
            dashboard_date_selected = None
    else:
        st.warning("Date column not found or not in datetime format in original data for dashboard date selection.")
        dashboard_date_selected = None

    if dashboard_date_selected:
        filter_date = pd.to_datetime(dashboard_date_selected)
        city_df_dashboard = df_original[(df_original['CITY'] == dashboard_city) & (df_original['date'] == filter_date)]
        
        st.markdown(f"### {dashboard_city.upper()} - TRAFFIC STATS")
        
        if city_df_dashboard.empty:
            st.warning(f"No daily data available for {dashboard_city} on {dashboard_date_selected.strftime('%B %d, %Y')}. Displaying overall city averages for stats below.")
            city_df_dashboard_display = df_original[df_original['CITY'] == dashboard_city]
            if city_df_dashboard_display.empty:
                st.error(f"No data found for {dashboard_city} at all in the original dataset.")
                st.stop()
            
            pop_density = city_df_dashboard_display['POPULATION DENSITY'].mean()
            tavg = city_df_dashboard_display['tavg'].mean()
            tmin = city_df_dashboard_display['tmin'].mean()
            tmax = city_df_dashboard_display['tmax'].mean()
            prcp = city_df_dashboard_display['prcp'].mean()
            aqi = city_df_dashboard_display['AQI_mean'].mean()
            pt_trips = city_df_dashboard_display['TOTAL PUBLIC TRANSPORT TRIP'].mean()
            congestion_avg = city_df_dashboard_display['congestion_index'].mean()
        else:
            st.markdown(f"##### {dashboard_date_selected.strftime('%B %d, %Y')}")
            pop_density = city_df_dashboard['POPULATION DENSITY'].mean()
            tavg = city_df_dashboard['tavg'].mean()
            tmin = city_df_dashboard['tmin'].mean()
            tmax = city_df_dashboard['tmax'].mean()
            prcp = city_df_dashboard['prcp'].mean()
            aqi = city_df_dashboard['AQI_mean'].mean()
            pt_trips = city_df_dashboard['TOTAL PUBLIC TRANSPORT TRIP'].mean()
            congestion_avg = city_df_dashboard['congestion_index'].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Population Density (people/km²)", f"{int(pop_density):,}")
        col2.metric("Temperature Range", f"{tmin:.1f}°C - {tmax:.1f}°C")
        col3.metric("Rainfall", f"{prcp:.0f} mm")

        col4, col5, col6 = st.columns(3)
        col4.metric("Average AQI", f"{aqi:.0f}")
        col5.metric("Public Transport Trips", f"{pt_trips:.0f}/day")
        col6.metric("Overall Daily Congestion", f"{congestion_avg:.0f}")

        st.subheader("Monthly Congestion Trend")
        if 'date' in df_original.columns and pd.api.types.is_datetime64_any_dtype(df_original['date']):
            monthly_avg = df_original[df_original['CITY'] == dashboard_city].groupby(df_original['date'].dt.to_period("M"))['congestion_index'].mean()
            if not monthly_avg.empty:
                monthly_avg.index = monthly_avg.index.to_timestamp()
                # Plotly line chart for monthly trend
                px_fig_monthly = px.line(monthly_avg.reset_index(), x='date', y='congestion_index',
                                         title=f"Monthly Congestion Trend in {dashboard_city}",
                                         labels={'date': 'Date', 'congestion_index': 'Congestion Index'},
                                         template=plotly_template,
                                         color_discrete_sequence=["#00D4FF"], # Vibrant blue
                                         height=600
                                        )
                font_color = "white" if plotly_template == "plotly_dark" else "black"
                px_fig_monthly.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
                st.plotly_chart(px_fig_monthly, use_container_width=True)
            else:
                st.info(f"No monthly congestion trend data available for {dashboard_city}.")
        else:
            st.warning("Date column not suitable for plotting monthly trend.")

    st.subheader(f"Interactive Traffic Congestion Map for {dashboard_city}")
    if gdf is not None and not gdf.empty:
        try:
            # Determine initial view state from the GeoDataFrame
            if not gdf.empty:
                geom_type = gdf.geometry.iloc[0].geom_type
                if geom_type == 'Point':
                    lat = float(gdf.geometry.y.mean())
                    lon = float(gdf.geometry.x.mean())
                else: # LineString or Polygon
                    lat = float(gdf.geometry.centroid.y.mean())
                    lon = float(gdf.geometry.centroid.x.mean())
            else:
                lat, lon = 0, 0 # Fallback

            # Updated Kepler.gl config to use Positron basemap.
            kepler_config = {
                "version": "v1",
                "config": {
                    "mapState": {
                        "latitude": lat,
                        "longitude": lon,
                        "zoom": 11
                    },
                    "mapStyle": {
                        "styleType": "positron" # Changed to Positron basemap
                    },
                    "visState": {
                        "layers": [
                            {
                                "id": "traffic_segments",
                                "type": "geojson",
                                "config": {
                                    "dataId": f"{dashboard_city}_data",
                                    "label": "Traffic Segments",
                                    "color": [0, 212, 255] if plotly_template == "plotly_dark" else [33, 150, 243], # Vibrant blue for segments
                                    "highlightColor": [255, 167, 38, 255], # Vibrant orange accent for highlight
                                    "columns": {
                                        "geojson": "geometry"
                                    },
                                    "isVisible": True,
                                    "visConfig": {
                                        "opacity": 0.8,
                                        "thickness": 0.5
                                    }
                                }
                            }
                        ]
                    }
                }
            }
            
            # Instantiate Kepler with an increased height and default config
            map_viewer = KeplerGl(height=800, config=kepler_config)
            
            # Add the full GeoDataFrame. User can now use the Kepler UI to configure layers.
            map_viewer.add_data(data=gdf, name=f"{dashboard_city}_data")

            map_html = map_viewer._repr_html_()
            
            # Display the map with an increased height
            st.components.v1.html(map_html, height=800, scrolling=True)
            st.info("Use the map controls to add layers, select data columns (e.g., monthly congestion), and customize the visualization.")

        except Exception as e:
            st.error(f"An unexpected error occurred while setting up Kepler.gl map: {e}")
    else:
        if geo_path and gdf is None:
             st.warning(f"GeoJSON data for {dashboard_city} could not be loaded. Map cannot be displayed. Please check the 'geojson' directory and file names.")
        elif gdf is not None and gdf.empty:
            st.warning(f"GeoJSON data for {dashboard_city} is empty. Cannot display map.")


# -------------------- Separator before “Traffic Policy Impact Analysis” --------------------
st.markdown('<hr class="main-separator" />', unsafe_allow_html=True)

def analyze_policy_impact(df_traffic, df_policies, days_window=300, plot_template="plotly_dark"):
    """
    Analyzes and visualizes the impact of traffic policies on congestion.
    Allows selection of cities and specific policies, displaying before/after metrics.
    """
    if df_policies is None or df_traffic is None or df_policies.empty or df_traffic.empty:
        st.info("Policy or traffic data is not available for impact analysis.")
        return

    policy_cities = df_policies['CITY'].unique().tolist()
    if not policy_cities:
        st.info("No cities found in the loaded policy data.")
        return

    with st.expander("Explore Policy Effects on Congestion", expanded=True):
        selected_city = st.selectbox("Select City for Policy Analysis", policy_cities, key="policy_city_select")

        city_policies = df_policies[df_policies['CITY'] == selected_city].copy()
        
        if city_policies.empty:
            st.info(f"No policies found for {selected_city}.")
            return
        
        city_policies['Policy_Label'] = city_policies['Date'].dt.strftime('%Y-%m-%d') + ' - ' + city_policies['Description'].fillna('No Description')

        policy_labels = city_policies['Policy_Label'].tolist()
        selected_policy_label = st.selectbox("Select a Policy", policy_labels, key="policy_select")

        if selected_policy_label:
            selected_policy_row = city_policies[city_policies['Policy_Label'] == selected_policy_label].iloc[0]
            policy_date = selected_policy_row['Date']
            policy_description = selected_policy_row['Description']

            st.write(f"**Analyzing Policy:** '{policy_description}' implemented on **{policy_date.strftime('%Y-%m-%d')}** in **{selected_city}**")

            start_date = policy_date - timedelta(days=days_window)
            end_date = policy_date + timedelta(days=days_window)

            analysis_data = df_original[
                (df_original['CITY'] == selected_city) &
                (df_original['date'] >= start_date) &
                (df_original['date'] <= end_date)
            ].copy()

            if analysis_data.empty:
                st.warning(f"No traffic data available for {selected_city} around the policy date {policy_date.strftime('%Y-%m-%d')} to analyze impact.")
                return

            analysis_data['days_from_policy'] = (analysis_data['date'] - policy_date).dt.days
            
            font_color = "white" if plot_template == "plotly_dark" else "black"

            # Use Plotly for policy impact plot
            px_fig = px.line(analysis_data, x='days_from_policy', y='congestion_index',
                             title=f"Congestion Trend around Policy Implementation in {selected_city}",
                             labels={'days_from_policy': f"Days from Policy Implementation (0 = {policy_date.strftime('%Y-%m-%d')})",
                                     'congestion_index': "Average Congestion Index"},
                             template=plot_template,
                             color_discrete_sequence=["#00D4FF"], # Vibrant blue line
                             height=800)
            
            # Add vertical line for policy date
            vline_color = "white" if plot_template == "plotly_dark" else "#333333"
            px_fig.add_vline(x=0, line_dash="dash", line_color=vline_color, annotation_text="Policy Implementation Date", annotation_position="top right")
            
            # Add shaded regions for before and after policy
            px_fig.add_shape(type="rect", x0=-days_window, y0=0, x1=0, y1=1, # y1=1 for normalized height
                             xref="x", yref="paper", fillcolor="#7C4DFF", opacity=0.1, layer="below", line_width=0,
                             name=f'{days_window} Days Before')
            px_fig.add_shape(type="rect", x0=0, y0=0, x1=days_window, y1=1, # y1=1 for normalized height
                             xref="x", yref="paper", fillcolor="#00D4FF", opacity=0.1, layer="below", line_width=0,
                             name=f'{days_window} Days After')

            # Update layout to show annotations and legend for shapes
            px_fig.update_layout(showlegend=True)
            px_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color)
            
            st.plotly_chart(px_fig, use_container_width=True)


            before_policy_data = analysis_data[analysis_data['days_from_policy'] < 0]
            after_policy_data = analysis_data[analysis_data['days_from_policy'] >= 0]

            avg_before = before_policy_data['congestion_index'].mean()
            avg_after = after_policy_data['congestion_index'].mean()

            st.markdown(f"### Summary of Impact for '{policy_description}'")
            if pd.notna(avg_before):
                st.metric(label=f"Avg. Congestion {days_window} Days BEFORE", value=f"{avg_before:.2f}")
            if pd.notna(avg_after):
                st.metric(label=f"Avg. Congestion {days_window} Days AFTER", value=f"{avg_after:.2f}", delta=f"{avg_after - avg_before:.2f}" if pd.notna(avg_before) else None)
            
            if pd.isna(avg_before) or pd.isna(avg_after):
                st.info("Insufficient data to calculate before/after change.")

st.header("Traffic Policy Impact Analysis")
analyze_policy_impact(df_original, df_policies, plot_template=plotly_template)
