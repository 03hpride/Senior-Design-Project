<?php
header('Content-Type: application/json');

$baseDir = dirname(__FILE__);
$rwisDir = realpath($baseDir . "/output/RWIS_data");

if ($rwisDir === false) {
    echo json_encode(["error" => "RWIS data directory not found."]);
    exit;
}

$parameterFile = $rwisDir . "/alertParameters.json";
$alertParameters = [];

if (file_exists($paramterFile)) {
    $json = file_get_contents($parameterFile);
    $alertParameters = json_decode($json, true);
    if (!is_array($alertParameters)) {
        $alertParameters = [];
    }
}

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

function loadCurrentConditions($csvDir) {
    $conditions = [];
    $files = glob($csvDir . "/current*_stable.csv");

    if (!empty($files)) {
        if (($h = fopen($files[0], "r")) !== false) {
            $header = fgetcsv($h);
            while (($row = fgetcsv($h)) !== false) {
                $conditions[] = array_combine($header, $row);
            }
            fclose($h);
        }
    }
    return $conditions;
}

function evaluateAlerts($alerts, $currentConditions) {
    $byStation = [];
    foreach ($currentConditions as $row) {
        $byStation[$row['station']] = $row;
    }

    foreach ($alerts as &$alert) {
        $alert['triggered'] = false;
        if (!$alert['is_enabled']) {
            continue;
        }

        $station = $alert['station_id'];
        $parameter = $alert['parameter_key'];

        if (!isset($byStation[$station])) continue;
        if (!isset($byStation[$station][$parameter])) continue;

        $value = $byStation[$station][$parameter];
        if (!is_numeric($value)) continue;

        switch ($alert['operator']) {
            case '>':
                $alert['triggered'] = $value > $alert['threshold_1'];
                break;
            case '<':
                $alert['triggered'] = $value < $alert['threshold_1'];
                break;
            case '>=':
                $alert['triggered'] = $value >= $alert['threshold_1'];
                break;
            case '<=':
                $alert['triggered'] = $value <= $alert['threshold_1'];
                break;
        }
    }
    return $alerts;
}

$stations = loadStations($rwisDir);
$currentConditions = loadCurrentConditions($rwisDir);
$alerts =[];
$evaluatedAlerts = evaluateAlerts($alerts, $currentConditions);

echo json_encode([ "stations" => $stations,
"currentConditions" => $currentConditions, "alertParameters" => $alertParameters,
"alerts" => $evaluatedAlerts ]);