<?php
$baseDir = __DIR__;
$combinedFile = $baseDir . "/rwis_processed.csv";
$metadataFile = $baseDir . "/rwis_metadata_processed.csv";

function loadStations($file) {
    if (!file_exists($file)) {
        return [];
    }

    $stations = [];
    if (($h = fopen($file, "r")) !== false) {
        $header = fgetcsv($h);
        $stationIndex = array_search("station", $header);

        while (($row = fgetcsv($h)) !== false) {
            if ($stationIndex !== false && !empty($row[$stationIndex])) {
                $stations[$row[$stationIndex]] = true;
            }
        }
        fclose($h);
    }
    return array_keys($stations);
}

function loadCurrentConditions($file) {
    if (!file_exists($file)) {
        return [];
    }

    $conditions = [];
    if (($h = fopen($file, "r")) !== false) {
        $header = fgetcsv($h);

        while (($row = fgetcsv($h)) !== false) {
            $conditions[] = array_combine($header, $row);
        }
        fclose($h);
    }
    return $conditions;
}

function loadParameters($file) {
    if (!file_exists($file)) {
        return [];
    }

    $parameters = [];
    if (($h = fopen($file, "r")) !== false) {
        $header = fgetcsv($h);
        $units = fgetcsv($h);  // Second row contains units
        
        // Only include these parameters
        $allowedParameters = [
            'essAirTemperature.1' => 'Air Temperature',
            'essRelativeHumidity' => 'Humidity',
            'essAvgWindSpeed' => 'Wind Speed',
            'essPrecipitationOneHour' => 'Precipitation'
        ];
        
        foreach ($header as $index => $columnName) {
            if (isset($allowedParameters[$columnName])) {
                $unit = isset($units[$index]) ? $units[$index] : "";
                $displayName = $allowedParameters[$columnName];
                $parameters[$columnName] = ["unit" => $unit, "display" => $displayName];
            }
        }
        fclose($h);
    }
    return $parameters;
}

function evaluateAlerts($alerts, $currentConditions) {
    $byStation = [];
    foreach ($currentConditions as $row) {
        if (isset($row['station'])) {
            $byStation[$row['station']] = $row;
        }
    }

    foreach ($alerts as &$alert) {
        $alert['triggered'] = false;
        if (!$alert['is_enabled']) continue;

        $station = $alert['station_id'];
        $parameter = $alert['parameter_key'];

        if (!isset($byStation[$station])) continue;
        if (!isset($byStation[$station][$parameter])) continue;

        $value = $byStation[$station][$parameter];
        if (!is_numeric($value)) continue;

        switch ($alert['operator']) {
            case '>': $alert['triggered'] = $value > $alert['threshold_1'];
            break;
            case '<': $alert['triggered'] = $value < $alert['threshold_1'];
            break;
            case '>=': $alert['triggered'] = $value >= $alert['threshold_1'];
            break;
            case '<=': $alert['triggered'] = $value <= $alert['threshold_1'];
            break;
        }
    }
    return $alerts;
}