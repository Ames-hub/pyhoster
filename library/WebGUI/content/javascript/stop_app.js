function stopInstance(appName) {
    fetch('http://localhost:987/instances/stop', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            app_name: appName,
            username: 'Ame',
            password: 'HellWillFearMyWrath'
        })
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response as needed
        console.log(data);
    })
    .catch(error => {
        alert("Error stopping instance: " + error);
    });
}

document.addEventListener('click', function(event) {
    if (event.target.classList.contains('appbuttons') && event.target.value === 'CLOSE') {
        // Gets the app's name and Removes the suffix " | Port (something)" from the app name
        const appName = String(event.target.parentNode.querySelector('h1').innerHTML).split(' ')[0]; 
        stopInstance(appName);
    }
});