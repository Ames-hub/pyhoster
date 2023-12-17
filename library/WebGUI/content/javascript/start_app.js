function startInstance(appName) {
    fetch('http://localhost:987/instances/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            app_name: appName,
            token: get_token()
        })
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response as needed
        console.log(data);
    })
    .catch(error => {
        alert("Error starting instance: " + error);
    });
}

document.addEventListener('click', function(event) {
    if (event.target.classList.contains('appbuttons') && event.target.value === 'START') {
        // App names can't have spaces. So we split the app name by spaces and get the first word.
        const appName = String(event.target.parentNode.querySelector('h1').innerHTML).split(' ')[0]; 
        startInstance(appName);
    }
});