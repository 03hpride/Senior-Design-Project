<?php
$baseDir = __DIR__;
$combinedFile = $baseDir . "/rwis_combined.csv";
$metadataFile = $baseDir . "/rwis_metadata_combined.csv";

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
        $parameterIndex = array_search("parameter", $header);
        $unitIndex = array_search("unit", $header);

        while (($row = fgetcsv($h)) !== false) {
            if ($parameterIndex !== false) {
                $key = $row[$parameterIndex];
                $unit = $unitIndex !== false ? $row[$unitIndex] : "";
                $parameters[$key] = ["unit" => $unit];
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