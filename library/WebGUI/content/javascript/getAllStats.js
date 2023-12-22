function getAllStats() {
    fetch('http://localhost:4000/instances/getall', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: get_token()
        })
    })
    .then(response => response.json())
    .then(data => {
        // Clear the apps_bar for each cycle through
        apps_bar.innerHTML = '';
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

                app_child.appendChild(document.createElement('h1')).innerHTML = `${key} | Port ${item['port']}`;
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

                // Adds the autoboot stat indicator
                if (item['autostart'] === true) {
                    app_child.appendChild(document.createElement('div')).classList.add('autoboot_on');
                }
                else {
                    app_child.appendChild(document.createElement('div')).classList.add('autoboot_off');
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
        console.log("Error in GetAllStats.js: " + error);
    });
}

getAllStats(); // Run initially
setInterval(getAllStats, 5000);

let autoboot_on = document.querySelectorAll('.autoboot_on');

for (let i = 0; i < autoboot_on.length; i++) {
    autoboot_on[i].addEventListener('click', function() {
        // Gets session token cookie
        sessiontoken = document.cookie.split('; ').find(row => row.startsWith('session')).split('=')[1];
        
        fetch('http://localhost:4000/instances/autoboot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token: sessiontoken,
                app_name: this.parentNode.querySelector('h1').innerHTML.split(' | ')[0],
                status: false
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data['status'] === 200) {
                this.classList.remove('autoboot_on');
                this.classList.add('autoboot_off');
            }
            else {
                console.log(data);
                alert("Something went wrong setting the autoboot. Check the console for more details.");
            }
        });
    }
    );
}

let autoboot_off = document.querySelectorAll('.autoboot_off');

window.addEventListener('DOMContentLoaded', (event) => {
    for (let i = 0; i < autoboot_off.length; i++) {
    autoboot_off[i].addEventListener('click', function() {
        fetch('http://localhost:4000/instances/autoboot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: 'Ame', // It's a debug username until we get the login system working.
                password: 'HellWillFearMyWrath',
                app_name: this.parentNode.querySelector('h1').innerHTML.split(' | ')[0],
                status: true
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data['status'] === 200) {
                this.classList.remove('autoboot_off');
                this.classList.add('autoboot_on');
            }
            else {
                console.log(data);
                alert("Something went wrong setting the autoboot. Check the console for more details.");
            }
        });
    }
    );
}
});