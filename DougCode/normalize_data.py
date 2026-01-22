import pandas as pd
import numpy as np
import json
import pickle
import os
import sys
import logging
import optparse
from datetime import datetime, timezone
from RWIS_utils import *
from RWIS_Headers import *

# File Path Configurations
output_path = "/home/www/public_html/WxShare/data/rwis/" # File Path for writing files (i.e. Sensor Data Output and Metadata Output)
pickle_path = "/home/www/public_html/WxShare/scripts/RWIS/allDistricts_metadata.pickle" # File Path for Persistent Metadata dictionary (currently same directory as this script)
json_path = "/home/www/public_html/WxShare/webroot/data/rwis_locations.json" # File Path for creating JSON file with metadata of all stations

# Setup logging configuration
logfile_path = '/home/www/public_html/WxShare/scripts/RWIS/logs/rwis_processing.log'
logging.basicConfig(format="%(UTC)s,%(LOCAL)s,1,%(msg)s", filename=logfile_path)
loggingEnabled = True # Change this to "False" to disable logging

def processData(file, district):

    rawData = pd.read_csv(filepath_or_buffer=file, dtype='str')
    rawData = rawData.drop('postmile', axis=1) # Remove 'postMile' since it isn't utilzed anywhere

    # setup Pandas DataFrame for metadata
    metadata_arrays = np.rot90(np.flip(rwisheaders['metadata'], axis = 1), 1)
    metadata_headers = pd.MultiIndex.from_arrays(arrays=metadata_arrays)
    metadataDF = pd.DataFrame(columns=metadata_headers)

    # setup Pandas DataFrame for sensor data
    sensor_data_arrays = np.rot90(np.flip(rwisheaders['sensor_data'], axis=1), 1)
    sensor_data_headers = pd.MultiIndex.from_arrays(arrays=sensor_data_arrays)
    sensorDataDF = pd.DataFrame(columns=sensor_data_headers)

    # Split metadata from rawData DataFrame
    metadata_names = ['district','locationName','nearbyPlace','longitude','latitude','elevation','direction','county',
                    'route','routeSuffix','postmilePrefix','alignment','milepost','inService','essNumTemperatureSensors',
                    'numEssPavementSensors','numEssSubSurfaceSensors']

    # Tries to find each of the above fields in the raw data and move them to the metadata DataFrame
    for name in metadata_names:
        try:
            metadataDF[name] = rawData.pop(name)
        except Exception as msg:
            if loggingEnabled: logError(name+' metadata column not found in datafile'+str(msg))

    # Convert Indexes to Station ID's
    stations = stationID(rawData['index'], district)
    sensorDataDF['station'] = stations
    metadataDF['station'] = stations

    # Convert date and time to UTC timestamp, local timestamp, and a localstring timestamp
    timeColumns = timeFromDateTime(rawData['recordDate'], rawData['recordTime'])
    sensorDataDF['timestamp:utc'] = timeColumns[1]
    sensorDataDF['timestamp:local'] = timeColumns[2]
    sensorDataDF['timestamp:localstring'] = timeColumns[0]
    metadataDF['timestamp:utc'] = timeColumns[1]
    metadataDF['timestamp:local'] = timeColumns[2]
    metadataDF['timestamp:localstring'] = timeColumns[0]

    # Convert Precipitation Start Times
    precipStartColumns = timeFromEpoch(rawData['essPrecipitationStartTime'])
    sensorDataDF['essPrecipitationStartTime_raw'] = rawData['essPrecipitationStartTime']
    sensorDataDF['essPrecipitationStartTime:utc'] = precipStartColumns[1]
    sensorDataDF['essPrecipitationStartTime:local'] = precipStartColumns[2]
    sensorDataDF['essPrecipitationStartTime:localstring'] = precipStartColumns[0]

    # Convert Precipitation End Times
    precipEndColumns = timeFromEpoch(rawData['essPrecipitationEndTime'])
    sensorDataDF['essPrecipitationEndTime_raw'] = rawData['essPrecipitationEndTime']
    sensorDataDF['essPrecipitationEndTime:utc'] = precipEndColumns[1]
    sensorDataDF['essPrecipitationEndTime:local'] = precipEndColumns[2]
    sensorDataDF['essPrecipitationEndTime:localstring'] = precipEndColumns[0]

    # Process All Other Columns Present in Raw Data
    for column in rawData.columns:
        raw_col = rawData[column] # Extract Column to work on
        if column in functionDict:
            sensorDataDF[column + "_raw"] = raw_col # Add raw column to new dataframe
            new_col = functionDict[column](raw_col.astype('str')) # Convert raw column using corresponding function
            sensorDataDF[column] = new_col          # Add converted column to dataframe

    # Export DataFrames to .csv files
    sensorDataDF.to_csv(output_path + 'current' + district + '_stable.csv', index=False) 
    metadataDF.to_csv(output_path + 'metadata' + district + '_stable.csv', index=False)

    # Export metadata to JSON file for use in webroot
    json_keys = ['station', 'timestamp:utc', 'timestamp:local', 'timestamp:localstring','district','locationName','nearbyPlace',
                'elevation','direction','county','route','routeSuffix','postmilePrefix','alignment','milepost','inService',
                'essReferenceHeight','essPressureHeight','essWindSensorHeight','essNumTemperatureSensors','numEssPavementSensors',
                'numEssSubSurfaceSensors','alert','alertAppliesTo','qc_pass']

    # Replace NaN values with empty strings
    JSONdataframe = metadataDF.copy().fillna('')
    # Convert values of certain columns to strings
    for i in range(len(json_keys)):
        JSONdataframe[json_keys[i]] = JSONdataframe[json_keys[i]].astype('str')

    # Get a list of icons used for stations in WeatherShare
    icon_list = []
    for i in range(len(sensorDataDF['essAirTemperature.1'])):
        try:
            if ((sensorDataDF['essAirTemperature.1'].values[i][0] != "Error:NTCIP") and 
                (sensorDataDF['essAirTemperature.1'].values[i][0] <= 32.0) or 
                (sensorDataDF['essSurfaceTemperature.1'].values[i][0] <= 32.0)):
                icon_list.append('rwiscold')
            else:
                icon_list.append('rwis')
        except:
            icon_list.append('rwis')
    JSONdataframe['icon'] = pd.Series(icon_list)

    # Covnert copy of metadata DataFrame to a dictionary
    dict = JSONdataframe.to_dict(orient="records")

    # Dictionary to change the keys in a dictionary into a shorter form
    key_map = {('station', 'id', 'string'): 'station',
            ('timestamp:utc', 'sec', 'epoch time'): 'timestamp:utc',
            ('timestamp:local', 'sec', 'epoch time'): 'timestamp:local',
            ('timestamp:localstring', 'time', 'time string'): 'timestamp:localstring',
            ('district', 'none', 'int'): 'district',
            ('locationName', 'none', 'text'): 'locationName',
            ('nearbyPlace', 'none', 'text'): 'nearbyPlace',
            ('longitude', 'deg', 'float'): 'longitude',
            ('latitude', 'deg', 'float'): 'latitude',
            ('elevation', 'ft', 'float'): 'elevation',
            ('direction', 'none', 'text'): 'direction',
            ('county', 'none', 'text'): 'county',
            ('route', 'none', 'text'): 'route',
            ('routeSuffix', 'none', 'text'): 'routeSuffix',
            ('postmilePrefix', 'none', 'text'): 'postmilePrefix',
            ('alignment', 'none', 'text'): 'alignment',
            ('milepost', 'mi', 'float'): 'milepost',
            ('inService', 'none', 'bool'): 'inService',
            ('essReferenceHeight', 'ft', 'float'): 'essReferenceHeight',
            ('essPressureHeight', 'ft', 'float'): 'essPressureHeight',
            ('essWindSensorHeight', 'ft', 'float'): 'essWindSensorHeight',
            ('essNumTemperatureSensors', 'none', 'int'): 'essNumTemperatureSensors',
            ('numEssPavementSensors', 'none', 'int'): 'numEssPavementSensors',
            ('numEssSubSurfaceSensors', 'none', 'int'): 'numEssSubSurfaceSensors',
            ('alert', 'none', 'bool'): 'alert',
            ('alertAppliesTo', 'none', 'text'): 'alertAppliesTo',
            ('qc_pass', 'none', 'bool'): 'qc_pass',
            ('icon', '', ''): 'icon'}


    json_dict = {}

    # Replace the keys in the dictionary with the short keys
    for i in range(len(dict)):
        json_dict.update({metadataDF.iloc[i, 0]: {key_map[k]: v for k, v in dict[i].items()}})

    # Code to merge metadata dictionaries, replacing old values with new where able
    def metadataMerge(old_dct, new_dct):
        res_dct = {}
        for key in set(list(old_dct.keys())+list(new_dct.keys())):
            try:
                if key in old_dct and key in new_dct:
                    res_dct[key] = new_dct[key]
                elif key in old_dct and not(key in new_dct):
                    res_dct[key] = old_dct[key]
                else:
                    res_dct[key] = new_dct[key]
            except Exception as msg:
                if loggingEnabled: logError('merge error: ' + str(msg),'')
                continue
        return res_dct

    # Load a .pickle file containing the metadata for all stations
    # Merge new data into the dictionary, and export back to a .pickle object
    def persistent_metadata(dct):
        full_dct = {}
        pdata = {}
        try:
            with open(pickle_path,'rb') as f:
                pdata = pickle.load(f)
        except Exception as msg:
            if loggingEnabled: logError('failed to process persistent data, no persistent data found on disk -> no old data to add:'+str(msg))
        full_dct = metadataMerge(pdata,dct)
        with open(pickle_path, 'wb') as f2:
            pickle.dump(full_dct, f2)
        return full_dct

    full_metadata_dict = {}
    full_metadata_dct = persistent_metadata(json_dict)
    json_str = json.dumps([full_metadata_dct])

    # Write dictionary to JSON file
    try:
        with open(json_path,'w') as fp:
            fp.write(json_str)
    except Exception as msg:
        if loggingEnabled: logError('failed to write metadata json:' + str(msg))

    # Begin exporting sensor data to JSON file
    times, stations = sensorDataDF[('timestamp:utc','sec','epoch time')], sensorDataDF[('station','id','string')]
    fileNames = []
    for i in range(len(times)):
        fileBase = datetime.fromtimestamp(times[i]).astimezone(timezone.utc)
        stationPath = output_path + stations[i]
        try:
            os.mkdir(stationPath)
        except:
            None

        # Tries to create file with the headers, if already created, then append data without headers

        # Process data files into daily files
        try:
            sensorDataDF.loc[[i]].to_csv(path_or_buf = stationPath + '/day_' + fileBase.strftime('%Y%m%d') + '0000.csv', index=False, mode='x')
        except:
            sensorDataDF.loc[[i]].to_csv(path_or_buf = stationPath + '/day_' + fileBase.strftime('%Y%m%d') + '0000.csv', index=False, mode='a', header=False)

        # Process data files into monthly files
        try:
            sensorDataDF.loc[[i]].to_csv(path_or_buf = stationPath + '/month_' + fileBase.strftime('%Y%m') + '000000.csv', index=False, mode='x')
        except:
            sensorDataDF.loc[[i]].to_csv(path_or_buf = stationPath + '/month_' + fileBase.strftime('%Y%m') + '000000.csv', index=False, mode='a', header=False)

        # Process data files into yearly files
        try:
            sensorDataDF.loc[[i]].to_csv(path_or_buf = stationPath + '/year_' + fileBase.strftime('%Y') + '00000000.csv', index=False, mode='x')
        except:
            sensorDataDF.loc[[i]].to_csv(path_or_buf = stationPath + '/year_' + fileBase.strftime('%Y') + '00000000.csv', index=False, mode='a', header=False)


def main():
    #Parser is used for providing arguments to the file when calling from a .sh file
    parser = optparse.OptionParser()
    parser.add_option('--district',dest='district')
    parser.add_option('--file',dest='data_file')
    options,args = parser.parse_args()
    district = options.district
    file = options.data_file

    # Call processing function
    processData(file, district)


if __name__ == '__main__':
    main()
    sys.exit(0)