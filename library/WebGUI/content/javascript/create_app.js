function createApp() {
    event.preventDefault()
    // Fetches from http://localhost:4000/instances/webcreate
    let do_autostart = document.getElementById('doautoboot').checked;
    let app_name = document.getElementById('create_appname').value;
    let port = document.getElementById('create_port').value;
    let description = document.getElementById('create_appdesc').value;

    if (app_name.includes(" ")) {
        alert("App name cannot contain spaces.");
        return;
    }

    fetch('http://localhost:4000/instances/webcreate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: get_token(),
            "app_name": app_name,
            "port": port,
            "do_autostart": do_autostart,
            "app_desc": description,
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data['msg'] === "Successful") {
            // refresh the app list
            getAllStats();
        }
        else {
            // If the app was not created successfully, then we can display an error message
            alert("The server encountered a problem. View console inspect for more details.");
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert("We encountered a critical problem. View console inspect for more details.");
    });
}