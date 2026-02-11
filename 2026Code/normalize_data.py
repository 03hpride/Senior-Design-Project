import pandas as pd
import numpy as np
import json
import optparse
from datetime import datetime, timezone
from RWIS_utils import *
from RWIS_Headers import *

def exportAlertParameters():
    """Export alert parameters to JSON string (returns dict instead of writing file)"""
    alertParameters = {}
    for name, unit, dtype in rwisheaders['sensor_data']:
        if dtype == 'float':
            alertParameters[name] = {
                "unit": unit, "dtype": dtype
            }
    return alertParameters

def processData(file, district):
    """Process a single district file and return the processed DataFrames"""
    
    print(f"Processing {file} for district {district}")
    
    rawData = pd.read_csv(filepath_or_buffer=file, dtype='str')
    rawData = rawData.drop('postmile', axis=1, errors='ignore')

    # setup Pandas DataFrame for metadata
    metadata_arrays = np.rot90(np.flip(rwisheaders['metadata'], axis=1), 1)
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

    for name in metadata_names:
        try:
            metadataDF[name] = rawData.pop(name)
        except Exception:
            pass

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
        raw_col = rawData[column]
        if column in functionDict:
            sensorDataDF[column + "_raw"] = raw_col
            new_col = functionDict[column](raw_col.astype('str'))
            sensorDataDF[column] = new_col

    return sensorDataDF, metadataDF


def main():
    parser = optparse.OptionParser()
    parser.add_option('--district', dest='district')
    parser.add_option('--file', dest='data_file')
    parser.add_option('--output', dest='output_file', default='rwis_combined.csv',
                      help='Output CSV filename (default: rwis_combined.csv)')
    parser.add_option('--metadata-output', dest='metadata_output', default='rwis_metadata_combined.csv',
                      help='Metadata output CSV filename (default: rwis_metadata_combined.csv)')
    options, args = parser.parse_args()
    
    # Export alert parameters (optional - can be saved if needed)
    alertParams = exportAlertParameters()
    
    all_sensor_data = []
    all_metadata = []

    # Process single file or multiple files
    if options.data_file and options.district:
        # Single file mode
        sensorDF, metaDF = processData(options.data_file, options.district)
        all_sensor_data.append(sensorDF)
        all_metadata.append(metaDF)
    else:
        # Multiple files mode
        import glob
        files = sorted(glob.glob("rwisStatusD*.csv"))
        
        if not files:
            print("No input files found.")
            return
        
        for f in files:
            d = f.replace("rwisStatus", "").replace(".csv", "")
            sensorDF, metaDF = processData(f, d)
            all_sensor_data.append(sensorDF)
            all_metadata.append(metaDF)
    
    # Combine all DataFrames
    if all_sensor_data:
        combined_sensor_data = pd.concat(all_sensor_data, ignore_index=True)
        combined_metadata = pd.concat(all_metadata, ignore_index=True)
        
        # Save to CSV files
        print(f"\nSaving combined sensor data to {options.output_file}")
        combined_sensor_data.to_csv(options.output_file, index=False)
        
        print(f"Saving combined metadata to {options.metadata_output}")
        combined_metadata.to_csv(options.metadata_output, index=False)
        
        print(f"\nTotal records processed: {len(combined_sensor_data)}")
        if ('station', 'id', 'string') in combined_sensor_data.columns:
            print(f"Total stations: {combined_sensor_data[('station', 'id', 'string')].nunique()}")
        
        print("\nProcessing complete!")
    else:
        print("No data processed.")


if __name__ == "__main__":
    main()
