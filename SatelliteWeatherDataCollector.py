
import requests
import bs4
import pandas as pd
import argparse
import WeatherApiKey
import json

from requests.api import request


def parse_args():
    """Parse and return the latitude and longitude arguments. 
    Used for testing in command line.
    """
    parser = argparse.ArgumentParser(
        description='Outputs satellite data for the given latitude and longitude')
    parser.add_argument("--lat", help="latitude", default="0")
    parser.add_argument("--long",  help="longitude", default="0")
    args = parser.parse_args()
    return args.lat, args.long


def scrape(lat, long):
    """Scrape html from heavens above ISS result site 

    Parameters:
    lat (str): latitude
    long (str): longitude

    Returns BeautiulSoup object containing html
    """
    # TODO: Allow user to input desired satellite, timezome, and altitude
    url = "https://www.heavens-above.com/PassSummary.aspx?satid=25544&lat=" + \
        lat+"&lng="+long+"&loc=Unnamed&alt=0&tz=EST"
    page = requests.get(url)
    return bs4.BeautifulSoup(page.content, 'lxml')


def parse_satellite_data(soup, col_names, indices):
    """Extract and store satellite data from scraped html [soup].

    Parameters:
    indices: iterable specifing which columns from site table are desired
    col_names: contains column names for returned dataframe

    Returns:
    pandas dataframe containing data with columns labeled by col_names
    """
    data = pd.DataFrame(columns=col_names)
    rows = soup.find_all('tr', attrs={'class': 'clickableRow'})
    # Parse data from page
    for row in rows:
        entry = []
        row_data = row.findAll('td')
        for i in indices:
            entry.append(row_data[i].text)
        data = data.append(pd.DataFrame([entry], columns=col_names))
    return data


def get_satellite_data(lat, long):
    """
    Collect and return satellite data from heavens above

    Retrieves date, start time, and end time data for each satellite pass

    Parameters:
    lat (str): latitude
    long (str): longitude

    Returns:
    pandas dataframe containing satellite data for next 10 days
    """
    soup = scrape(lat, long)
    indices = [0, 2, 8]
    names = ("Date", "Start time", "End time")
    return parse_satellite_data(soup, names, indices)

    # TODO: Allow users to request specific information about the satellite rather than/ in addition to just printing a table


def get_weather_data(lat, long, test):
    """
    Collect and return weather information using tomorrow.io API

    Collects data about temperature, cloud cover, preciption intensity,  
    and precipitation type for next 15 days

    Parameters:
    lat (str): latitude
    long (str): longitude
    test (boolean): When false, sends API call. When true, use saved API response

    Returns:
    pandas dataframe containing weather data for next 10 days 
    """
    if (not test):
        url = "https://api.tomorrow.io/v4/timelines?location="+long+","+lat + \
            "&fields=temperature,cloudCover,precipitationIntensity,precipitationType,&timesteps=1d&units=metric&apikey=" + \
            WeatherApiKey.getApiKey()
        data = requests.get(url).json()
    else:
        file = open("exampleTomorrowResponse.json")
        data = json.load(file)
    columns = ("Temperature", "Cloud Cover (%)",
               "Precipitation Intensity", "Precipitation Type")
    result = pd.DataFrame()
    intervals = data["data"]["timelines"][0]["intervals"]
    for day in intervals:
        day["values"]["weather date"] = day["startTime"]
        result = result.append(day["values"], ignore_index=True)
    return result


# Used to find length of month for mergeData()
month_end = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def merge_data(sat_data, weather_data):
    """Merge satellite data and weather data into a single table.

    For each entry in sat_data, find the corresponding entry in weather_data and 
    concatenate it to that row (prioritize satellite data over weather data).
    """
    result = sat_data
    first_weather_time = weather_data.loc[0, "weather date"]
    start_day = int(first_weather_time[8:10])
    month = int(first_weather_time[5:7])
    end_month = month_end[month]
    concat_weather = pd.DataFrame()
    for i in range(len(sat_data)):
        day = int(sat_data.loc[i, "Date"][0:2])
        index = day - start_day if (day-start_day >
                                    0) else end_month-start_day + day
        concat_weather = concat_weather.append(weather_data.iloc[index])
    concat_weather = concat_weather.reset_index(drop=True)
    result = pd.concat((sat_data, concat_weather), axis=1)
    return result


def get_data(lat, long):
    """Fetch satellite and weather data and return html table of results."""
    sat_data = get_satellite_data(lat, long)
    sat_data = sat_data.reset_index(drop=True)
    weather_data = get_weather_data(lat, long, test=True)
    result = merge_data(sat_data, weather_data)
    return result.to_html(index=False)


if __name__ == "__main__":
    get_data("41", "-74")
