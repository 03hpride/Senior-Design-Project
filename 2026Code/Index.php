<?php
try {
    $db = new PDO("sqlite:rwis_alerts.db");
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Database connection failed: " . $e->getMessage());
}

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
    if (empty($_POST['alert_id']) || empty($_POST['name'])) {
        die("Error: Missing Information");
    }

    $stmt = $db->prepare("
        UPDATE alerts
        SET name = :name, updated_at_utc = strftime('%s','now')
        WHERE alert_id = :id");

    $stmt->execute([
        ':name' => $_POST['name'],
        ':id' => $_POST['alert_id']
    ]);
    header("Location: index.php");
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

$user_id = 1;

$stmt = $db->prepare("
    SELECT alert_id, name, station_id, parameter_key, operator,
           threshold_1, threshold_2, is_enabled
    FROM alerts
    WHERE user_id = :user_id
    ORDER BY created_at_utc DESC");

$stmt->execute([
    ':user_id' => $user_id
]);

$alerts = $stmt->fetchAll(PDO::FETCH_ASSOC);
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
<header>
    <nav class="navbar">
        <div class="container nav-inner">
            <a class="navbar-brand" href="#">Weather Share Notification Center</a>
            <div class="nav-buttons">
                <button>Dashboard</button>
                <button>Account</button>
                <button>Preferences</button>
                <form action="Login.php" method="get" style="display:inline;">
                    <button type="submit">Login</button>
                </form>
            </div>
        </div>
    </nav>
</header>
<main>
<div class="container top-actions">
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
                data-name="<?= htmlspecialchars($alert['name']) ?>">
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
</main>



<div id="new_alert_modal" class="modal">
    <div class="modal_content">
        <span class="close">&times;</span>
        <h2>New Alert</h2>
        <form method="post">

            <label>Name</label>
            <input type="text" name="name" required>
            <label>Station</label>
            <input type="text" name="station_id" required>
            <label>Parameter</label>
            <input type="text" name="parameter_key" required>
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
        document.getElementById("edit_alert_id").value =
            btn.dataset.id;
        document.getElementById("edit_alert_name").value =
            btn.dataset.name;
        openModal(editModal);
    };
});

document.querySelectorAll(".delete-btn").forEach(btn => {
    btn.onclick = () => {
        document.getElementById("delete_alert_id").value =
            btn.dataset.id;
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