<?php
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}
?>

<header>
    <nav class="navbar">
        <div class="container nav-inner">
            <a class="navbar-brand" href="index.php">
                Weather Share Notification Center
            </a>
            <?php if (isset($_SESSION['username'])): ?>
                    <span class="nav-welcome">
                        Welcome, <?= htmlspecialchars($_SESSION['username']) ?>
                    </span>
            <?php endif; ?>
        </div>
            <div class="nav-buttons">
                <a href="Index.php"><button>Dashboard</button></a>
                <a href="Account.php"><button>Account</button></a>
                <?php if (isset($_SESSION['username'])): ?>
                        <a href="Logout.php"><button>Logout</button></a>
                    <?php else: ?>
                        <a href="Login.php"><button>Login</button></a>
                <?php endif; ?>
            </div>
        </div>
    </nav>
</header>
