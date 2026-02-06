import os
import requests
import normalize_data

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

    for url in URLS:
        name = url.split("/")[-1]                 # rwisStatusD02.csv
        district = name.replace("rwisStatus", "").replace(".csv", "")  # D02
        path = os.path.join(here, name)

        print("downloading", name)
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)

        print("converting", name, "district", district)
        normalize_data.processData(path, district)

    print("done")

if __name__ == "__main__":
    main()
