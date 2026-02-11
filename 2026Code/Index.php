<?php
require_once 'load_rwis_data.php';

try {
    $db = new PDO("sqlite:rwis_alerts.db");
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Database connection failed: " . $e->getMessage());
}

$combinedFile = __DIR__ . "/rwis_combined.csv";
$metadataFile = __DIR__ . "/rwis_metadata_combined.csv";
$stations = loadStations($combinedfile);
$currentConditions = loadCurrentConditions($combinedFile);
$parameters = loadParameters($metadataFile);

if (isset($_POST['create_alert'])) {

    if (
        empty($_POST['name']) ||
        empty($_POST['station_id']) ||
        empty($_POST['parameter_key']) ||
        empty($_POST['operator'])
    ) {
        die("Error: Missing Information");
    }

    $stmt = $db->prepare("
        INSERT INTO alerts
        (user_id, name, station_id, parameter_key, operator, threshold_1, threshold_2, is_enabled, created_at_utc, updated_at_utc)
        VALUES
        (1, :name, :station_id, :parameter_key, :operator, :threshold_1, :threshold_2, 1, strftime('%s','now'), strftime('%s','now'))
    ");

    $stmt->execute([
        ':name' => $_POST['name'],
        ':station_id' => $_POST['station_id'],
        ':parameter_key' => $_POST['parameter_key'],
        ':operator' => $_POST['operator'],
        ':threshold_1' => $_POST['threshold_1'] ?? null,
        ':threshold_2' => null
    ]);

    header("Location: index.php");
    exit;
}

if (isset($_POST['edit_alert'])) {
    if (
        empty($_POST['alert_id']) ||
        empty($_POST['name']) ||
        empty($_POST['station_id']) ||
        empty($_POST['parameter_key']) ||
        empty($_POST['operator'])
    ) {
        die("Erorr: Missing Information");
    }

    $stmt = $db->prepare("UPDATE alerts SET name =:name,
    station_id = :station_id, parameter_key = :parameter_key,
    operator = :operator, threshold_1 = :threshold_1,
    updated_at_utc = strftime('%s','now') WHERE alert_id = :id");

    $stmt->execute([':name' => $_POST['name'],
    ':station_id' => $_POST['station_id'], ':parameter_key' => $_POST['parameter_key'],
    ':operator' => $_POST['operator'], ':threshold_1' => $_POST['threshold_1'] ?? null,
    ':id' => $_POST['alert_id']]);

    header("Location: Index.php");
    exit;
}

if (isset($_POST['delete_alert'])) {
    if (empty($_POST['alert_id'])) {
        die("Error: Missing Information");
    }
    $stmt = $db->prepare("DELETE FROM alerts WHERE alert_id = :id");
    $stmt->execute([
        ':id' => $_POST['alert_id']
        ]);
    header("Location: index.php");
    exit;
}

$stmt = $db->prepare("SELECT alert_id, name, station_id, parameter_key, operator, threshold_1, is_enabled
FROM alerts WHERE user_id = 1 ORDER BY created_at_utc DESC");

$stmt->execute();
$alerts = $stmt->fetchAll(PDO::FETCH_ASSOC);

$currentConditions = loadCurrentConditions(__DIR__ . "/output/rwis");
$alerts = evaluateAlerts($alerts, $currentConditions);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Weather Share Notification Center</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="stylesheet.css">
</head>
<body>
    <?php include 'navbar.php'; ?>
<main class="container">
<div class="top-actions">
    <button id="new_alert_btn" class="new">New Alert</button>
</div>
<div class="table-responsive">
<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Station</th>
            <th>Parameter</th>
            <th>Condition</th>
            <th>Status</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>

<?php foreach ($alerts as $alert): ?>
<tr>
    <td><?= htmlspecialchars($alert['name']) ?></td>
    <td><?= htmlspecialchars($alert['station_id']) ?></td>
    <td><?= htmlspecialchars($alert['parameter_key']) ?></td>
    <td>
        <?= htmlspecialchars($alert['operator']) ?>
        <?= htmlspecialchars($alert['threshold_1']) ?>
    </td>
    <td><?= $alert['is_enabled'] ? 'Enabled' : 'Disabled' ?></td>
    <td>
        <div class="actions">
            <button
                class="action-btn edit-btn"
                data-id="<?= $alert['alert_id'] ?>"
                data-name="<?= htmlspecialchars($alert['name']) ?>"
                data-station="<?= htmlspecialchars($alert['station_id']) ?>"
                data-parameter="<?= htmlspecialchars($alert['parameter_key']) ?>"
                data-operator="<?= htmlspecialchars($alert['operator']) ?>"
                data-threshold="<?= htmlspecialchars($alert['threshold_1']) ?>">
                <img src="edit.png">
            </button>
            <button
                class="action-btn delete-btn"
                data-id="<?= $alert['alert_id'] ?>">
                <img src="delete.png">
            </button>
        </div>
    </td>
</tr>
<?php endforeach; ?>
    </tbody>
</table>
</div>
<section class="conditions">
    <h2>Current Conditions</h2>
    <table>
        <thead>
            <tr>
                <th>Station</th>
                <th>Air Temperature</th>
                <th>Humidity</th>
                <th>Wind Speed</th>
                <th>Precipitation</th>
                <th>Last Updated</th>
            </tr>
        </thead>
        <tbody>

<?php foreach (array_slice($currentConditions, 0, 5) as $c): ?>
    <tr>
        <td><?= htmlspecialchars($c['station']) ?></td>
        <td><?= htmlspecialchars($c['essAirTemperature.1'] ?? '-') ?></td>
        <td><?= htmlspecialchars($c['essRelativeHumidity'] ?? '-') ?></td>
        <td><?= htmlspecialchars($c['essAverageWindSpeed'] ?? '-') ?></td>
        <td><?= htmlspecialchars($c['essPrecipRate'] ?? '-') ?></td>
        <td><?= htmlspecialchars($c['timestampt:localstring'] ?? '-') ?></td>
    </tr>
    <?php endforeach; ?>
    </tbody>
</table>
</setion>
    </main>

<div id="new_alert_modal" class="modal">
    <div class="modal_content">
        <span class="close">&times;</span>
        <h2>New Alert</h2>
        <form method="post">

            <label>Name</label>
            <input type="text" name="name" required>
            <label>Station</label>
            <select name="station_id" required>
                <option value="">Select Station</option>
                <?php foreach ($stations as $station): ?>
                    <option value="<?= htmlspecialchars($station) ?>">
                        <?= htmlspecialchars($station) ?>
                    </option>
                <?php endforeach; ?>
            </select>
            <label>Parameter</label>
            <select name="parameter_key" required>
                <option value="">Select Parameter</option>
                <?php foreach ($parameters as $key => $meta): ?>
                    <option value="<?= htmlspecialchars($key) ?>">
                        <?= htmlspecialchars($key) ?> (<?= htmlspecialchars($meta['unit']) ?>)
                    </option>
                <?php endforeach; ?>
            </select>
            <label>Operator</label>
                <select name="operator" required>
                    <option value="">Select</option>
                    <option value=">">&gt;</option>
                    <option value="<">&lt;</option>
                    <option value=">=">&ge;</option>
                    <option value="<=">&le;</option>
                </select>
            <label>Threshold</label>
            <input type="number" step="any" name="threshold_1">
        <div class="modal_buttons">
            <button type="submit" name="create_alert">Create</button>
            <button type="button" class="cancel">Cancel</button>
        </div>
        </form>
    </div>
</div>
<div id="edit_alert_modal" class="modal">
    <div class="modal_content">
        <span class="close">&times;</span>
        <h2>Edit Alert</h2>
        <form method="post">
            <input type="hidden" name="alert_id" id="edit_alert_id">
            <label>Name</label>
            <input type="text" name="name" id="edit_alert_name" required>
            <label>Station</label>
            <select name="station_id" id="edit_alert_station" required>
                <?php foreach ($stations as $station): ?>
                    <option value="<?= htmlspecialchars($station) ?>">
                        <?= htmlspecialchars($station) ?>
                    </option>
                <?php endforeach; ?>
            </select>
            <label>Parameter</label>
            <select name="parameter_key" id="edit_alert_parameter" required>
                <?php foreach ($parameters as $key => $meta): ?>
                    <option value="<?= htmlspecialchars($key) ?>">
                        <?= htmlspecialchars($key) ?> (<?= htmlspecialchars($meta['unit']) ?>)
                    </option>
                <?php endforeach; ?>
            </select>
            <label>Operator</label>
            <select name="operator" id="edit_alert_operator" required>
                <option value=">">&gt;</option>
                <option value="<">&lt;</option>
                <option value=">=">&ge;</option>
                <option value="<=">&le;</option>
            </select>
            <label>Threshold</label>
            <input type="number" setp="any" name="threshold_1" id="edit_alert_threshold">
        <div class="modal_buttons">
            <button type="submit" name="edit_alert">Save</button>
            <button type="button" class="cancel">Cancel</button>
        </div>
    </form>
</div>
</div>
<div id="delete_alert_modal" class="modal">
    <div class="modal_content">
        <span class="close">&times;</span>
        <h2>Delete Alert</h2>
            <p>Are you sure you want to delete this alert?</p>
        <form method="post">
            <input type="hidden" name="alert_id" id="delete_alert_id">
        <div class="modal_buttons">
            <button type="submit" name="delete_alert" class="danger">Delete</button>
            <button type="button" class="cancel">Cancel</button>
        </div>
    </form>
</div>
</div>

<script>
const openModal = m => m.style.display = "flex";
const closeModal = m => m.style.display = "none";
const newModal = document.getElementById("new_alert_modal");
const editModal = document.getElementById("edit_alert_modal");
const deleteModal = document.getElementById("delete_alert_modal");

document.getElementById("new_alert_btn").onclick = () => openModal(newModal);
document.querySelectorAll(".close, .cancel").forEach(btn => {
    btn.onclick = () => {
        document.querySelectorAll(".modal").forEach(m => closeModal(m));
    };
});

document.querySelectorAll(".edit-btn").forEach(btn => {
    btn.onclick = () => {
        edit_alert_id.value = btn.dataset.id;
        edit_alert_name.value = btn.dataset.name;
        edit_alert_station.value = btn.dataset.station;
        edit_alert_parameter.value = btn.dataset.parameter;
        edit_alert_operator.value = btn.dataset.operator;
        edit_alert_threshold.value = btn.dataset.threshold;
        openModal(editModal);
    };
});

document.querySelectorAll(".delete-btn").forEach(btn => {
    btn.onclick = () => {
        delete_alert_id.value = btn.datasetid;
        openModal(deleteModal);
    };
});

window.onclick = e => {
    document.querySelectorAll(".modal").forEach(m => {
        if (e.target === m) {
            closeModal(m);
        }
    });
};
</script>
</body>
</html>