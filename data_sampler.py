# -*- coding: utf-8 -*-
"""
Small script to sample daily data from your netatmo weather stations. 
All data are stored to .csv files, seperated by station/modules and type of 
measurement. 

This script bases on the lnetatmo module and your own Netatmo-Applet 
(https://dev.netatmo.com).
See https://github.com/philippelt/netatmo-api-python regarding the lnetatmo
documentation. 

Created on Fri Dec 25 20:14:34 2020

@author: jmoeckel
"""
import os
import datetime
import inspect
import json

import pandas as pd
import lnetatmo
from lnetatmo import WeatherStationData as WSD

THISDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

CONFIG_FILENAME = 'authorization.json'
STOREDIR =  os.path.join(THISDIR, 'data')

def _init_wsd(auth:dict=None):
    """ initializes an authorized WeatherStationData object. 
    
    To authorize, either use input config or a file config.json
    

    Parameters
    ----------
    config : dict, optional
        Contains authorization parameters. Mandatory keys:
            
            clientID: str
                client id for your app on dev.netatmo.com
            clientSecret: str
                corresponding secret for your app on dev.netatmo.com
            username: str
                username, which you use to login to your netatmo-account
            password: str
                corresponding password
            scope: str
                scope of your request, by default use "read_station"            
            
        If none, configuration is loaded from auth.json (which must have keys  
        accordingly to the above description). The default is none.

    Raises
    ------
    FileNotFoundError
        if neither input auth is given AND file auth.json does not exist

    Returns
    -------
    WSD
        an authorized WeatherStationData object.

    """
    
    if not auth:        
        try:
            with open(os.path.join(THISDIR, CONFIG_FILENAME)) as f:
                auth = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError('Either use input config or store your authorization details in a file auth.json')
           
    authorization = lnetatmo.ClientAuth(auth)
    wsd = WSD(authorization)
    
    return wsd

def _data_sampler_device(wsd:WSD, base:str, device:dict, date:str, dp:str):
    """ sample data for a station or a module for one day (00:01 till 23:59)
    
    All available data from a station or module are sampled with maximal 
    resolution. 
    
    Sampled data are stored in .csv files (two columns, first column datetime,
    second one is the value). Files are stored in given dirpath or - if not
    given - in directory "data".
    
    Parameters
    ----------
    wsd : WSD
         an authorized WeatherStationData object.
    base : str
        ID of the main station.
    device : dict
        parametrization of a device, either a station or a module. If its a 
        module, it must be a child of the station defined by "base"
    date : str
        date of interest, mandatory format "YYYY-MM-DD".
    dp : str
        dirpath, where to store the generated csv files.

    Returns
    -------
    None.     

    """   
    name = device['module_name']
    ident = device['_id']
    mtypes = device['data_type']
    
    # print('\n' + name + ':')
    tstart = lnetatmo.toEpoch(f'{date}_00:00:01')
    tend = lnetatmo.toEpoch(f'{date}_23:59:59')
        
    for mtype in mtypes:
        # print(mtype)
        resp = wsd.getMeasure(device_id=base, module_id=ident, scale='max', mtype=mtype, date_begin=tstart, date_end=tend)
        data = resp['body']
        
        datetime = [lnetatmo.toTimeString(key) for key in data.keys()]
        values = [value[0] for value in data.values()]
        
        df = pd.DataFrame({'DateTime': datetime, 'Value': values})
        
        df.to_csv(os.path.join(dp, f'{date}_{name}_{mtype}.csv'), index=False)


def data_sampler_stations(wsd:WSD=None, date:str=None, dp_save:str=None):
    """ Samples data for all stations and their associated modules for one day
    
    More or less a wrapper for _data_sampler_device. This is used, as the 
    "station" dictionary (list-entry of the response of WSD.stations) is not 
    consistent with respect to the data structure of data regarding the station 
    itsself and data regarding the associated modules are stored inconsistently).
    
    Parameters
    ----------
    wsd : WSD, optional
        an authorized WeatherStationData object. If none, this object is
        is initialized. Default is none.
    date : str, optional
        date of interest, mandatory format "YYYY-MM-DD". If none, "date" is set
        to yesterday. The default is None.
    dp_save : str, optional
        dirpath, where to store the generated csv files. If none, files are 
        saved to directory "data". Default is none

    Returns
    -------
    None.

    """
    
    if not wsd:
        wsd = _init_wsd()
    
    if not date:
       date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    if not dp_save:
        dp_save = STOREDIR
    
    stations = wsd.stations
    for station in stations.values():
        # first the station itself ...
        base = station['_id'] 
        # print(station['station_name'])
        _data_sampler_device(wsd, base, station, date)
        
        # ... then its modules
        for module in station['modules']:
            _data_sampler_device(wsd, base, module, date)


def data_sampler_stations_period(date_start:str, dp_save:str=None):
    """ Samples data for all stations and their associated modules for a period
    of days. 
    
    More or less a wrapper for data_sampler_stations()
    

    Parameters
    ----------
    date_start : str
        Date in the past. Data are sampled from this date till yesterday. 
        Mandatory date format "YYYY-MM-DD".
    dp_save : str, optional
        dirpath, where to store the generated csv files. If none, files are 
        saved to directory "data". Default is none

    Returns
    -------
    None.

    """
    
    if not dp_save:
        dp_save = STOREDIR
    
    # initialize the WeatherStationObject once
    wsd = _init_wsd()
    
    # determine how many days in the past the sampling starts
    d0 = datetime.datetime.strptime(date_start, "%Y-%m-%d")
    d1 = datetime.datetime.now()    
    dt = d1 - d0
    n = dt.days
    
    # actually sample data for several days
    while n>0: 
        sday = str((datetime.datetime.now() - datetime.timedelta(days=n)).strftime('%Y-%m-%d'))  
        print(sday)
        data_sampler_stations(wsd=wsd, date=sday, dp_save=dp_save)
        n = n-1
        