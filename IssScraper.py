
import requests
import bs4
import pandas as pd
import argparse


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
    return data.to_html(index=False)


# Must specify which columns in heavens above table to grab. The columns are in the following order:
#"Date", "Brightness", "Start Time", "Start Alt.", "Start Az.", "Hightest Pt. Time", "Hightest Pt. Alt.", "Hightest Pt. Az.", "End Time", "End Alt.", "End Az.", "Pass type"
def getSatelliteData(lat, long):
    soup = scrape(lat, long)
    # create data frame
    indices = [0, 2, 8]
    names = ("Date", "Start time", "End time")
    return parse_data(soup, names, indices)

    # TODO: Allow users to request specific information about the satellite rather than/ in addition to just printing a table


if __name__ == "__main__":
    scrape("0", "0")
