
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


def scrape(lat, long, satellite):
    """Scrape html from heavens above ISS result site 

    Parameters:
    lat (str): latitude
    long (str): longitude

    Returns BeautiulSoup object containing html
    """
    # TODO: Allow user to input desired satellite, timezome, and altitude
    sat_id = "25544"
    if (satellite == "ISS"):
        sat_id = "25544"
    elif (satellite == "Tiangong"):
        sat_id = "48274"
    elif (satellite == "X-37B"):
        sat_id = "45606"
    elif (satellite == "N. Korean satellite"):
        sat_id = "39026"
    elif (satellite == "Hubble Space Telescope"):
        sat_id = "20580"
    elif (satellite == "Envisat"):
        sat_id = "27386"
    url = "https://www.heavens-above.com/PassSummary.aspx?satid="+sat_id+"&lat=" + \
        lat+"&lng="+long+"&loc=Unnamed&alt=0&tz=UCT"
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


def get_satellite_data(lat, long, satellite):
    """
    Collect and return satellite data from heavens above

    Retrieves date, start time, and end time data for each satellite pass

    Parameters:
    lat (str): latitude
    long (str): longitude

    Returns:
    pandas dataframe containing satellite data for next 10 days
    """
    indices = [0, 2, 8]
    names = ("Date", "Start time", "End time")
    if satellite == "default":
        return pd.DataFrame(columns=names)
    else:
        soup = scrape(lat, long, satellite)
        return parse_satellite_data(soup, names, indices)

    # TODO: Allow users to request specific information about the satellite rather than/ in addition to just printing a table


def convert_precip_type(precip_num):
    if precip_num == 0:
        return "None"
    if precip_num == 1:
        return "Rain"
    if precip_num == 2:
        return "Snow"
    if precip_num == 3:
        return "Freezing Rain"
    if precip_num == 4:
        return "Ice Pellets"


def get_weather_data(lat, long, test):
    """
    Collect and return weather information using tomorrow.io API

    Collects data about temperature, preciption intensity,  
    and precipitation type for next 15 days

    Parameters:
    lat (str): latitude
    long (str): longitude
    test (boolean): When false, sends API call. When true, use saved API response

    Returns:
    pandas dataframe containing weather data for next 10 days 
    """
    if (not test):
        url = "https://api.tomorrow.io/v4/timelines?location="+lat+","+long + \
            "&fields=temperature,precipitationIntensity,precipitationType,&timesteps=1d&units=imperial&apikey=" + \
            WeatherApiKey.getApiKey()
        data = requests.get(url).json()
    else:
        file = open("exampleTomorrowResponse.json")
        data = json.load(file)
    columns = ("Temperature",
               "Precipitation Intensity", "Precipitation Type")
    result = pd.DataFrame()
    intervals = data["data"]["timelines"][0]["intervals"]
    for day in intervals:
        day["values"]["Weather Date"] = day["startTime"]
        day["values"]["precipitationType"] = convert_precip_type(
            day["values"]["precipitationType"])
        day["values"]["temperature"] = str(day["values"]["temperature"]) + \
            "\N{DEGREE SIGN}"
        result = result.append(day["values"], ignore_index=True)
    result = result.rename(columns={
        "precipitationIntensity": "Precipitation Intensity (in/hr)", "precipitationType": "Precipitation Type", "temperature": "Temperature (\N{DEGREE SIGN}F)"})
    return result


# Used to find length of month for mergeData()
month_end = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def merge_data(sat_data, weather_data):
    """Merge satellite data and weather data into a single table.

    For each entry in sat_data, find the corresponding entry in weather_data and 
    concatenate it to that row (prioritize satellite data over weather data).
    """
    result = sat_data
    columns = ["Date", "Start time", "End time",
               "Temperature (\N{DEGREE SIGN}F)", "Precipitation Type", "Precipitation Intensity (in/hr)"]
    if sat_data.empty:
        return pd.DataFrame(columns=columns)
    else:
        first_weather_time = weather_data.loc[0, "Weather Date"]
        start_day = int(first_weather_time[8:10])
        month = int(first_weather_time[5:7])
        end_month = month_end[month]
        concat_weather = pd.DataFrame()
        for i in range(len(sat_data)):
            day = int(sat_data.loc[i, "Date"][0:2])
            index = day - start_day if (day-start_day >=
                                        0) else end_month-start_day + day
            concat_weather = concat_weather.append(weather_data.iloc[index])
        concat_weather = concat_weather.reset_index(drop=True)
        result = pd.concat((sat_data, concat_weather), axis=1)
        result = result[columns]
        return result


def get_data(lat, long, satellite):
    """Fetch satellite and weather data and return html table of results."""
    sat_data = get_satellite_data(lat, long, satellite)
    sat_data = sat_data.reset_index(drop=True)
    weather_data = get_weather_data(lat, long, test=True)
    result = merge_data(sat_data, weather_data)
    return result.to_html(index=False)


if __name__ == "__main__":
    get_data("0", "0", "default")
