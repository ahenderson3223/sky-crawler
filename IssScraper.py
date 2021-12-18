
import requests
import bs4
import pandas as pd

# use sample url for now and then change to use user input (coordinates and satellite)
# scrape site
url = "https://www.heavens-above.com/PassSummary.aspx?satid=25544&lat=43.2484&lng=-75.7749&loc=Unnamed&alt=0&tz=EST"
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
