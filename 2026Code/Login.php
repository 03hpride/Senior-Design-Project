<!doctype html>
<html lang="en">
    <head>
         <title>Weather Share Notification Sign Up</title>
        <link rel="stylesheet" href="stylesheet.css">
    </head>
    <body>
        <?php include 'navbar.php'; ?>
        <main>
            <center>
                <h2 style="padding: 20px;">Login to Your Account</h2>
            </center>

            <div class="containerbutton-row">
                <form action="authenticate.php" method="post">
                    <label for="username">Username:</label><br>
                    <input type="text" id="username" name="username" required><br><br>
                    <label for="password">Password:</label><br>
                    <input type="password" id="password" name="password" required><br><br> <!-- password_hash() -->
                    <input type="submit" value="Login">
                </form>

                <p stlye="text-align: center; margin-top: 15px; font-size: 0.9rem;">
                    Don't have an account?
                    <a href="Signup.php" style="color:#2563eb; text-decoration: none; font-weight: 600;">
                        Sign Up
                    </a>
                </p>
            </div>
        </main>
        <footer>
        </footer>
    </body>
</html>
