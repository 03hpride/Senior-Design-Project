<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Weathe Share Notification Sign Up</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="stylesheet.css">
    </head>
    <body>
        <header>
            <nav class="navbar">
                <div class="container nav-inner">
                    <a class="navbar-brand" href="Index.php">Weather Share Notification Center</a>
                </div>
            </nav>
        </header>

        <main>
            <center><h2 style="padding: 20px;">Create Account</h2></center>
            <div class="containerbutton-row">
                <form action="register.php" method="post">
                    <label for="username">Username</label><br>
                    <input type="text" id="username" name="username" required><br><br>
                    <label for="email">Email</label><br>
                    <input type="text" id="email" name="email" required><br><br>
                    <label for="password">Password</label><br>
                    <input type="password" id="password" name="password" required><br><br>
                    <label for="confirm_password">Confirm Password</label><br>
                    <input type="password" id="confirm_password" name="confirm_password" required><br><br>
                    <input type="submit" value="Sign Up">
                </form>

                <p stlye="text-align: center; margin-top: 15px; font-size: 0.9rem;">
                    Already have an account?
                    <a href="Login.php" style="color:#2563eb; text-decoration: none; font-weight: 600;">
                        Login
                    </a>
                </p>
            </div>
        </main>
        <footer>
        </footer>
    </body>
</html>