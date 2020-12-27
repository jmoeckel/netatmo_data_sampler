# netatmo_data_sampler
Sample data from your netatmo stations (including its modules) and store them as csv files

## Description
Small script to sample daily data from your netatmo weather stations. 
All data are stored to .csv files, seperated by station/modules and type of measurement. 

This script bases on the lnetatmo module and your own Netatmo-Applet (https://dev.netatmo.com).
See https://github.com/philippelt/netatmo-api-python regarding the lnetatmodocumentation.

## Uage
1. Store your credential in a file auth.json (clientID, ClientSecret, username, password, scope)
2. copy the script
3. Import as a python module and use method data_sampler_stations() to sample data for one day (by default: yesterday), or data_sampler_stations_period() to sample data for several days till yesterday (input: past start date)

The script and its methods are documented (especially with respect to inputs). 
