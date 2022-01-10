# SkyCrawler

A webapp to help satellite observers by displaying satellite and weather forecasting information.

This project allows satellite observers to access information about when a satellite can be viewed at their location over the next 10 days. It also provides weather location so observers can determine which passes will be visible.

The inspiration for this project comes from my own experience viewing satellites. Instead of referencing two different sites for satellite pass information and weather information, I wanted to create a single source for planning satellite viewings. I also wanted to gain more experience with sending API requests and with web development.

# Project Status

The simple functionality has been completed. Users can input a location (in terms of coordinates) or simply allow the app to access their current location. Users can select a satellite. Then, SkyCrawler displays satellite passes at that location for the next 10 days, along with the weather information for those days.

The website currently is not being hosted, but screenshots can be found below:

# Project Screenshots

![screenshot](https://github.com/ahenderson3223/sky-crawler/blob/main/IssScreenshot.png?raw=true)

# Credits

This tool scrapes Heaven's Above (https://www.heavens-above.com/) for satellite information. All credit for satellite information goes to Heaven's Above.

This tool also utilizes Tomorrow.io's weather api (https://www.tomorrow.io/weather-api/). All credit for weather information goes to Tomorrow.io.
