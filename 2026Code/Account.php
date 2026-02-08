<?php
session_start();

if(!isset($_SESSION['user_id'])) {
    header("Location: Login.php");
    exit;
}

try {
    $db = new PDO("sqlite:rwis_alerts.db");
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Database connection failed.");
}

$user_id = $_SESSION['user_id'];
$message = "";
$error = "";

$stmt = $db->prepare("SELECT user_id, username, password_hash, rols, is_enabled FROM users WHERE user_id = :id");
$stmt->execute([':id' => $user_id]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);

if(!user) {
    die("User not found.");
}

if (isset($_POST['update_password'])) {
    if (!password_verify($_POST['current_password'], $user['password_hash'])) {
        $error = "Current password is incorrect.";
    } elseif ($_POST['new_password'] !== $_POST['confirm_password']) {
        $error = "New password do not match.";
    } elseif (strlen($_POST['new_password']) <8) {
        $error = "Password must be at least 8 characters.";
    } else {
        $hashed = password_hash($_POST['new_password'], PASSWORD_DEFAULT);
        $stmt = $db->prepare("UPDATE users SET password_hash = :hash WHERE user_id = :id");
        $stmt->execute([':hash' => $hashed, ':id' => $user_id]);
        $message = "Password updated!";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Account</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<?php include 'navbar.php'; ?>
<main class="container">
    <h1>Account Settings</h1>
    <?php if ($message): ?>
        <p class="success"><?= htmlspecialchars($message) ?></p>
        <?php endif ?>
    <?php if ($error): ?>
        <p class="error"><?= htmlspecialchars($error) ?></p>
    <?php endif ?>

    <section>
        <h2>Profile</h2>
        <p><strong>Username:</strong> <?= htmlspecialchars($user['username']) ?></p>
        <p><strong>Status:</strong> <?= htmlspecialchars($user['is_enabled'] ? 'Enabled' : 'Disabled') ?></p>
    </section>

    <section>
        <h2>Change Password</h2>
        <form method="post">
            <label>Current Password</label>
            <input type="password" name="current_password" required>
            <label>New Password</label>
            <input type="password" name="new_password" required>
            <label>Confirm New Password</label>
            <input type="password" name="confirm_password" required>
            <button type="submit" name="update_password">Update Password</button>
        </form>
    </section>
</main>
</body>
</html>