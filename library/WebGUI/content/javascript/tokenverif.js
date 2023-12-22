// This is the token that will be used to authenticate the user. Gotten from the login page
function get_token() {
    let sessionCookie = document.cookie.split('; ').find(row => row.startsWith('session'));
    return sessionCookie ? sessionCookie.split('=')[1] : null;
}

// Sends the user to the login page if the token is not found or an error occurs while getting the token
function sendToLogin() {
    let tkn = get_token()
    fetch('http://localhost:4000', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            token: tkn
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status != "ok") {
            console.log(data.status)
            window.location.href = "login.html";
        }
    })

    if (tkn == undefined || tkn == null || tkn == "") {
        window.location.href = "login.html";
    }
}

sendToLogin() // Do it initially before loop
setInterval(() => {
    sendToLogin();
}, 5000);