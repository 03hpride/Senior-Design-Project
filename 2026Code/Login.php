<!doctype html>
<html lang="en">
    <head>
         <title>Weather Share Notification Sign Up</title>
        <link rel="stylesheet" href="stylesheet.css">
    </head>
    <body>
        <header>
            <center>
            <nav
                class="navbar navbar-expand-sm navbar-light bg-light"
            >
                <div class="container">
                    <a class="navbar-brand" href="#"><center>Weather Share Notification Center</center></a>
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="collapsibleNavId">
                        <!-- <ul class="navbar-nav me-auto mt-2 mt-lg-0">
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
                       </ul> -->
                    </div>
                </div>
            </nav>
            </center>
        </header>
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
            </div>
        </main>
        <footer>
        </footer>
    </body>
</html>
