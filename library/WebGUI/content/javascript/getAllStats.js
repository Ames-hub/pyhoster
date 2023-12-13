function getAllStats() {
    fetch('http://localhost:987/instances/getall', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: 'Ame', // It's a debug username until we get the login system working.
            password: 'HellWillFearMyWrath'
        })
    })
    .then(response => response.json())
    .then(data => {
        
        // Iterate through the properties of the object
        for (let key in data) {
            if (data.hasOwnProperty(key)) {
                let item = data[key];
                
                let app_child = document.createElement('div');
                // SRC is the PyHoster logo for now
                app_child.appendChild(document.createElement('img')).src = "PyhostLogo.png";
                // Adds the img to the ".appicon" class for css
                app_child.querySelector('img').classList.add('appicon');
                app_child.classList.add('app');

                app_child.appendChild(document.createElement('h1')).innerHTML = key;
                // Adds H1 to the ".appname" class for css
                app_child.querySelector('h1').classList.add('appname');

                // Adds the START and STOP submit buttons
                app_child.appendChild(document.createElement('input')).type = "submit";
                app_child.appendChild(document.createElement('input')).type = "submit";
                // Adds the START and STOP text to the buttons
                app_child.querySelectorAll('input')[0].value = "START";
                app_child.querySelectorAll('input')[1].value = "CLOSE";
                // Adds the appbuttons class to them
                app_child.querySelectorAll('input')[0].classList.add('appbuttons');
                app_child.querySelectorAll('input')[1].classList.add('appbuttons');

                if (item['warden'] === true) {
                    // Adds an element with class name "warden_shield". From ther, Style.css does the job by adding a shield image to it.
                    app_child.appendChild(document.createElement('div')).classList.add('warden_on');
                }
                else {
                    app_child.appendChild(document.createElement('div')).classList.add('warden_off');
                }

                if (item['running'] === true) {
                    app_child.style.boxShadow = "-10px -10px 0px 0px green";
                }
                else {
                    app_child.style.boxShadow = "-10px -10px 0px 0px red";
                }
                apps_bar.appendChild(app_child);
            }
        }
    })
    .catch(error => {
        alert("Error: " + error);
    });
}

getAllStats(); // Run initially
// setInterval(getAllStats, 10000);
