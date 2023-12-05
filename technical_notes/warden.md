# WARDEN
Basic description: Warden is a basic lockout system that allows you to lock out users from a specific webpage.

It works by sending a user to a webpage that asks for a password.<br>
If the password is correct, it will send them to the webpage they were trying to access.<br>
Otherwise, it will return a 403 (forbidden) error.

## How to use
1. Pick a web app's PAGE (not the full website, unless wanted) to lock out
2. Run `enter warden`
It will prompt you for the app name, provide it.
3. If you haven't tinkered with the settings and enabled it<br>
you'll see the following text
```
Status for app: (APP_NAME)
WARDEN IS CURRENTLY INACTIVE.
I am currently protecting 0 pages.
Those pages have been accessed UNKNOWN times.

warden>
```
4. To enable warden, run `enable`. To disable, run `disable` (run help for more commands, as there are more)
5. To add a page to the list of protected pages, run `addpage` and follow the prompts. (use rempage to remove a page)

## Technical Mumbo Jumbo below
Warden works by accessing a json file called "config.json" within the instances folder of the app.<br>
It stores the settings for warden in there, its pin, where its enabled or not and the pages that are protected.<br>
It also stores the amount of times each page has been accessed.

When a user tries to access a page, it will check if warden is enabled, if it is, it will check if the page is protected.<br>
If it is, it will send the user to the warden page, if not, it will send them to the page they were trying to access.

When a user enters the pin, it will check if the pin is correct, if it is, it will send them to the page they were trying to access.<br>
If not, it will return a 403 (forbidden) error.

## How does it get the password
It gets the valid pin from the aforementioned pin file, which is stored in the instances folder of the app.<br>
How it gets the sent pin is by using a weird sort of "redirect" method. Where it sends the user<br>
"library/webpages/warden_login.html" and then asks them for the pin there.<br>
That website will then redirect them to `"(host_name)/(file to access)/warden?pin=(pin)"`<br>
If `"warden?pin=(pin)"` is Found in the url (not looking FOR the pin, just its existance) it will send them to the page they were trying to access by removing "warden?pin=(pin)" from the requested path that it sent over (as it would be requesting that file, if it didn't)<br>
and continuing as normal as if warden never checked.

## Security Concerns
I want to make something VERY clear.<br>
Warden is not meant to be a full security system, it is meant to be a basic lockout system.<br>
It is not meant to be used as a full security system, and should not be used as such.<br>
It will keep out the basic user, but if someone looks into it at all they will be able to bypass it<br>
<hr>
Long story short, DONT DEPEND ON IT TO KEEP EVERYTHING SAFE!<br>