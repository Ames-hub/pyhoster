function login() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    fetch("http://localhost:987/userman/login", {
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
        }
        else {
            if (data['status'] == 423) {
                alert("Login failed. Your account has been locked by Administrators.");
            }
            else if (data['status'] == 403) {
                alert("Login failed. Is your Username or password is incorrect?");
            }
            else if (data['status'] == 401) {
                alert("Invalid login details sent.");
            }
        }
    })
}