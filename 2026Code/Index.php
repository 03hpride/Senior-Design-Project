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
        <title>Weather Share Notification Sign Up</title>
        <!-- Required meta tags -->
        <meta charset="utf-8" />
        <meta
            name="viewport"
            content="width=device-width, initial-scale=1, shrink-to-fit=no"
        />

        <!-- Bootstrap CSS v5.2.1 -->
        <!--<link
            href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
            rel="stylesheet"
            integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN"
            crossorigin="anonymous"
        /> --> 
        <link rel="stylesheet" href="stylesheet.css">
    </head>

    <body>
        <header>
            <center><nav
                class="navbar navbar-expand-sm navbar-light bg-light"
            >
                <div class="container">
                    <a class="navbar-brand" href="#"><center>Weather Share Notification Center</center></a>
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="collapsibleNavId">
                        <ul class="navbar-nav me-auto mt-2 mt-lg-0">
                            <button
                                type="button"
                                class="btn btn-primary"
                                style="margin-right: 10px;"
                            >
                                Dashboard
                            </button>
                        </ul>
                        <ul class="navbar-nav me-auto mt-2 mt-lg-0">
                            <button
                                type="button"
                                class="btn btn-primary"
                                style="margin-right: 10px;"
                            >
                                Account
                            </button>
                        </ul>
                        <ul class="navbar-nav me-auto mt-2 mt-lg-0">
                            <button
                                type="button"
                                class="btn btn-primary"
                                style="margin-right: 10px;"
                            >
                                Preferences
                            </button>
                        </ul>
                        <ul class="navbar-nav me-auto mt-2 mt-lg-0">
                            <button
                                type="button"
                                class="btn btn-primary"
                                style="margin-right: 10px;"
                            >
                                Logout
                            </button>
                        </ul>
                    </div>
                </div>
            </nav>
            </center>
        </header>
        <main>
            <div class="container button-row">
                <button id="newAlert">New Alert</button>
                <div id="newAlertModal" class="modal">
                    <div class="modalContent">
                        <span class="close">&times;</span>
                        <h2>Create New Alert</h2>
                        <form action="saveAlert.php" method="post">
                            <label for="alertName">Alert Name</label>
                            <input type="text" id="alertName" name="alertName" required>
                            <div class="modalButtons">
                                <button type="submit">Save Alert</button>
                                <button type="button" id="cancelAlert">Cancel</button>
                            </div>
                        </form>
                <button class="danger">
                    Delete Alert
                </button>
                <button>
                    Edit Alert
                </button>

            <div
                class="table-responsive"
            >
                <table
                    class="table table-primary"
                    style="margin-top: 10px;"
                >
                    <thead>
                        <tr>
                            <th scope="col">Column 1</th>
                            <th scope="col">Column 2</th>
                            <th scope="col">Column 3</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="">
                            <td scope="row">Item</td>
                            <td>Item</td>
                            <td>Item</td>
                        </tr>
                        <tr class="">
                            <td scope="row">Item</td>
                            <td>Item</td>
                            <td>Item</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
        </main>
        <footer>
        </footer>
        <!-- Bootstrap JavaScript Libraries -->
        <script
            src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js"
            integrity="sha384-I7E8VVD/ismYTF4hNIPjVp/Zjvgyol6VFvRkX/vR+Vc4jQkC+hVqc2pM8ODewa9r"
            crossorigin="anonymous"
        ></script>

        <script
            src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.min.js"
            integrity="sha384-BBtl+eGJRgqQAUMxJ7pMwbEyER4l1g+O15P+16Ep7Q9Q+zqX6gSbd85u4mG4QzX+"
            crossorigin="anonymous"
        ></script>
    </body>
</html>