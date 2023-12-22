function login() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    fetch("http://localhost:4000/userman/login", {
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
            window.location.replace("https://localhost:4040/");
        }
        else {
            if (data['status'] == 423) {
                alert("Login failed.\nYour account was locked by Administrators or Warden.");
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