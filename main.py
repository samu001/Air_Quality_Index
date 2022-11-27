import streamlit as st
import requests
import folium
from streamlit_folium import folium_static

# General API data
API_KEY = "1c87e736-9460-46c3-87f7-bb057635dd8f"


# Functions

# Function to fetch data and return an array of the query word
@st.cache
def fetch_data(url, query):
    res = requests.get(url).json()
    arr = [""]

    for item in res['data']:
        arr.append(item[query])
    return arr


# Function to interpret aqi
def find_aqi_rank(aqi):
    if 0 <= aqi <= 50:
        return "Good"
    elif 51 <= aqi <= 100:
        return "Moderate Good"
    elif 101 <= aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif 151 <= aqi <= 200:
        return "Unhealthy"
    else:
        return "Very Unhealthy"


# Function to display weather information
def display_weather_data(res):
    city = res['data']['city']
    tempC = res['data']['current']['weather']['tp']
    tempF = round(tempC * 1.8 + 32)
    pressure = res['data']['current']['weather']['pr']
    hum = res['data']['current']['weather']['hu']
    aqi = res['data']['current']['pollution']['aqius']

    aqi_rank = find_aqi_rank(aqi)

    st.write("Temperature in ", city, " is ", tempC, "°C /", tempF, "°F")
    st.write("The pressure is ", pressure, " hPa")
    st.write("Humidity is ", hum, "%")
    st.write("The air quality index is currently ", aqi, "which is considered", aqi_rank)


# Function to display a map of the given coordinates
def map_creator(latitude, longitude):
    m = folium.Map(location=[latitude, longitude], zoom_start=40)
    folium.Marker([latitude, longitude], popup="Station", tooltip="Station").add_to(m)
    folium_static(m)


# SideBar
selectedTab = st.sidebar.selectbox("Select a Tab", ["Country/State/City", "Nearest City", "Latitude/Longitude"],
                                   index=0)

st.header("⛅ Weather around the World")

if selectedTab == "Country/State/City":

    st.subheader("List Selector")

    try:
        # Get Countries
        url = "https://api.airvisual.com/v2/countries?key=" + API_KEY
        countries = fetch_data(url, 'country')
        country = st.selectbox('Select a Country', countries, index=0)  # usa is default

        if country:
            # Get States
            url = "https://api.airvisual.com/v2/states?country=" + country + "&key=" + API_KEY
            states = fetch_data(url, 'state')

            state = st.selectbox('Select a State', states, index=0)

            if state:
                # Get Cities
                url = "https://api.airvisual.com/v2/cities?state=" + state + "&country=" + country + "&key=" + API_KEY
                cities = fetch_data(url, 'city')

                city = st.selectbox('Select a City', cities, index=0)

                if city:
                    # Get Weather Data
                    url = "https://api.airvisual.com/v2/city?city=" + city + "&state=" + state + "&country=" + country + "&key=" + API_KEY
                    res = requests.get(url).json()
                    display_weather_data(res)
    except:
        st.warning("Data not available for State/City or too many API calls in 1 minute")


elif selectedTab == 'Nearest City':

    st.subheader("Nearest City")

    if st.button('Get Data'):
        try:
            res = requests.get("https://api.airvisual.com/v2/nearest_city?key=" + API_KEY).json()
            latitude = res['data']['location']['coordinates'][1]
            longitude = res['data']['location']['coordinates'][0]

            display_weather_data(res)
            map_creator(latitude, longitude)
        except:
            st.warning("Too many API calls in 1 minute")

elif selectedTab == 'Latitude/Longitude':

    st.subheader('Find by Latitude/Longitude')
    st.markdown('**Examples:**')
    st.write("Miami: 25.76, -80.20 | Rome: 41.90, 12.50")

    latitude = str(st.number_input('Insert a latitude (-90 to 90)', min_value=-90.0, max_value=90.0, value=0.0))
    longitude = str(st.number_input('Insert a longitude (-180 to 180)', min_value=-180.0, max_value=180.0, value=0.0))
    url = "https://api.airvisual.com/v2/nearest_city?lat=" + latitude + "&lon=" + longitude + "&key=" + API_KEY

    if st.button('Get Data'):

        try:
            res = requests.get(url).json()
            st.write("Closest city to the coordinates is ", res['data']['city'])
            display_weather_data(res)

            map_creator(latitude, longitude)
        except:
            st.warning("Not station found for coordinates or too many API calls in 1 minute")
