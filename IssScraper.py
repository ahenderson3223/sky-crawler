
import requests
import bs4
import pandas as pd
import sys
import argparse

# parse arguments
parser = argparse.ArgumentParser(
    description='Outputs satellite data for the given latitude and longitude')
parser.add_argument("--lat", help="latitude", default="0")
parser.add_argument("--long",  help="longitude", default="0")
args = parser.parse_args()

# scrape site
# TODO: Allow user to input desired satellite, timezome, and altitude
url = "https://www.heavens-above.com/PassSummary.aspx?satid=25544&lat=" + \
    args.lat+"&lng="+args.long+"&loc=Unnamed&alt=0&tz=EST"
page = requests.get(url)
soup = bs4.BeautifulSoup(page.content, 'lxml')

# create data frame
rows = soup.find_all('tr', attrs={'class': 'clickableRow'})
columns = ("Date", "Brightness", "Start Time", "Start Alt.", "Start Az.", "Hightest Pt. Time",
           "Hightest Pt. Alt.", "Hightest Pt. Az.", "End Time", "End Alt.", "End Az.", "Pass type")
data = pd.DataFrame(columns=columns)

# Parse data from page
for row in rows:
    entry = []
    for td in row.findAll('td'):
        entry.append(td.text)
    data = data.append(pd.DataFrame([entry], columns=columns))

# Display
print(data)

# TODO: Allow users to request specific information about the satellite rather than/ in addition to just printing a table
