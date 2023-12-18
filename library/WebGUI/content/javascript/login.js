function login() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    fetch("http://localhost:4045/userman/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data['status'] == 200) {
            document.cookie = "session=" + data['session'] + "; SameSite=lax";
            // Changes the button's text to "Enter" and redirects to the home page
            document.getElementById("login_text").innerHTML = "Enter";
            window.location.replace("https://{-{hostName}-}:4040/");
        }
        else {
            if (data['status'] == 423) {
                alert("Login failed. Your account was locked by Administrators or Automoderation.");
            }
            else if (data['status'] == 403) {
                alert("Login failed. Is your Username or password incorrect?");
            }
            else if (data['status'] == 401) {
                alert("Invalid login details sent.");
            }
        }
    })
}