<?php
function loadStations($csvDir) {
    $stations = [];

    foreach (glob($csvDir . "/current*_stable.csv") as $file) {
        if (($h = fopen($file, "r")) !== false) {
            $header = fgetcsv($h);
            $idx = array_search('station', $header);

            while (($row = fgetcsv($h)) !== false) {
                if ($idx !== false && !empty($row[$idx])) {
                    $stations[$row[$idx]] = true;
                }
            }
            fclose($h);
        }
    }

    return array_keys($stations);
}
