
import requests
import bs4
import pandas as pd
import argparse
import WeatherApiKey

from requests.api import request


def parse_args():
    # parse arguments
    parser = argparse.ArgumentParser(
        description='Outputs satellite data for the given latitude and longitude')
    parser.add_argument("--lat", help="latitude", default="0")
    parser.add_argument("--long",  help="longitude", default="0")
    args = parser.parse_args()
    return args.lat, args.long


def scrape(lat, long):
    # scrape site
    # TODO: Allow user to input desired satellite, timezome, and altitude
    url = "https://www.heavens-above.com/PassSummary.aspx?satid=25544&lat=" + \
        lat+"&lng="+long+"&loc=Unnamed&alt=0&tz=EST"
    page = requests.get(url)
    return bs4.BeautifulSoup(page.content, 'lxml')


def parse_data(soup, col_names, indices):
    data = pd.DataFrame(columns=col_names)
    rows = soup.find_all('tr', attrs={'class': 'clickableRow'})
    # Parse data from page
    for row in rows:
        entry = []
        row_data = row.findAll('td')
        for i in indices:
            entry.append(row_data[i].text)
        data = data.append(pd.DataFrame([entry], columns=col_names))

    # convert to html
    return data


# Must specify which columns in heavens above table to grab. The columns are in the following order:
#"Date", "Brightness", "Start Time", "Start Alt.", "Start Az.", "Hightest Pt. Time", "Hightest Pt. Alt.", "Hightest Pt. Az.", "End Time", "End Alt.", "End Az.", "Pass type"
def getSatelliteData(lat, long):
    soup = scrape(lat, long)
    # create data frame
    indices = [0, 2, 8]
    names = ("Date", "Start time", "End time")
    return parse_data(soup, names, indices)

    # TODO: Allow users to request specific information about the satellite rather than/ in addition to just printing a table


def getWeatherData(lat, long):
    url = "https://api.tomorrow.io/v4/timelines?location="+long+","+lat + \
        "&fields=temperature,cloudCover,precipitationIntensity,precipitationType,&timesteps=1d&units=metric&apikey=" + \
        WeatherApiKey.getApiKey()
    data = requests.get(url).json()
    columns = ("Temperature", "Cloud Cover (%)",
               "Precipitation Intensity", "Precipitation Type")
    result = pd.DataFrame()
    intervals = data["data"]["timelines"][0]["intervals"]
    for day in intervals:
        result = result.append(
            day["values"], ignore_index=True)
    #result = result.rename(columns=columns)
    return result


def getData(lat, long):
    sat_data = getSatelliteData(lat, long)
    sat_data = sat_data.reset_index(drop=True)
    weather_data = getWeatherData(lat, long)
    weather_data = weather_data.reset_index(drop=True)
    result = pd.concat((sat_data, weather_data), axis=1)
    sat_length = len(sat_data.index)
    weather_length = len(weather_data.index)
    result = result.drop(result.index[min(sat_length, weather_length):])
    return result.to_html(index=False)


if __name__ == "__main__":
    print("hi")
    getData("41", "-74")
