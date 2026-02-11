import os
import requests
import normalize_data
import pandas as pd

URLS = [
    "https://cwwp2.dot.ca.gov/data/d2/rwis/rwisStatusD02.csv",
    "https://cwwp2.dot.ca.gov/data/d3/rwis/rwisStatusD03.csv",
    "https://cwwp2.dot.ca.gov/data/d6/rwis/rwisStatusD06.csv",
    "https://cwwp2.dot.ca.gov/data/d8/rwis/rwisStatusD08.csv",
    "https://cwwp2.dot.ca.gov/data/d9/rwis/rwisStatusD09.csv",
    "https://cwwp2.dot.ca.gov/data/d10/rwis/rwisStatusD10.csv",
]

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    
    all_sensor_data = []
    all_metadata = []

    for url in URLS:
        name = url.split("/")[-1]                 # rwisStatusD02.csv
        district = name.replace("rwisStatus", "").replace(".csv", "")  # D02
        path = os.path.join(here, name)

        print(f"Downloading {name}...")
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)
            print(f"Downloaded {name}")
        except Exception as e:
            print(f"Failed to download {name}: {e}")
            continue

        print(f"Processing {name} for district {district}...")
        try:
            sensorDF, metaDF = normalize_data.processData(path, district)
            all_sensor_data.append(sensorDF)
            all_metadata.append(metaDF)
            print(f"Processed {name} - {len(sensorDF)} records")
        except Exception as e:
            print(f"Failed to process {name}: {e}")
            continue

    # Combine all data
    if all_sensor_data:
        combined_sensor_data = pd.concat(all_sensor_data, ignore_index=True)
        combined_metadata = pd.concat(all_metadata, ignore_index=True)
        
        # Save combined files
        output_sensor = "rwis_processed.csv"
        output_metadata = "rwis_metadata_processed.csv"
        
        print(f"Saving processed sensor data to {output_sensor}")
        combined_sensor_data.to_csv(output_sensor, index=False)
        
        print(f"Saving processed metadata to {output_metadata}")
        combined_metadata.to_csv(output_metadata, index=False)
        
        print(f"  Total records: {len(combined_sensor_data)}")
        
        # Get unique stations from the multi-index column
        if ('station', 'id', 'string') in combined_sensor_data.columns:
            unique_stations = combined_sensor_data[('station', 'id', 'string')].nunique()
            print(f"  Total unique stations: {unique_stations}")
        
        print(f"    - {output_sensor}")
        print(f"    - {output_metadata}")
    else:
        print("\nNo data was successfully processed.")

if __name__ == "__main__":
    main()
