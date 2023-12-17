let status_bar = document.getElementById('status_detector');
let status_text = document.getElementById('status_text');

function updateStatus(status_bar, status_text) {
    fetch("http://localhost:987", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            token: get_token()
        })
    })
    .then(response => response.json()) // convert response to text
    .then(data => {
        if (data['status'] == "ok") {
            status_bar.style.backgroundColor = "green";
            status_text.innerHTML = "Online";
            return true;
        }
        else {
            status_bar.style.backgroundColor = "red";
            status_text.innerHTML = "Offline";
            console.log(data) // log what went wrong with the server 
            return false;
        }
    })
    .catch(() => {
        status_bar.style.backgroundColor = "red";
        status_text.innerHTML = "Offline";
        return false;
    });
}

let delay = 10000;
updateStatus(status_bar, status_text);
setInterval(function() {
    if (!updateStatus(status_bar, status_text)) {
        delay = 30000; // Backoff if server is offline
    }
}, delay);