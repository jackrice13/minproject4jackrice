### INF601 - Advanced Programming in Python
### Jack Rice
### Mini Project 4
 
 
# Project Title
 
SecLog.
 
## Description
 
SecLog is a Django-based Security Operations Center (SOC) incident response platform that allows security teams to log, track, and resolve cybersecurity incidents. Built with a relational database backend, it captures key investigative details including affected assets, indicators of compromise, MITRE ATT&CK mappings, and chain-of-custody evidence. The platform features role-based user authentication, a severity-aware incident dashboard, and a terminal-inspired dark UI — developed as a practical capstone project for a graduate cybersecurity program. 
## Getting Started
 
### Dependencies
 
Django
BootStrap
 
### Installing
 
Install dependencies
```
pip install -r requirements.txt
```
Change Directory
```
cd seclog
```
Run migrations
```
python manage.py migrate
```
Loading seed data
```
python manage.py loaddata seed_data.json
 ```
### Executing program
 
To Start Website 
```
python manage.py runserver
```

User List

Super User 
Username:Admin
Password:Admin

Generic User
Username:Bob
Password:justaword123
 

## Help
 
Any advise for common problems or issues.
```
command to run if program contains helper info
```
 
## Authors
 

 
## Version History

* 0.1
    * Initial Release
 

## Acknowledgments
 
Inspiration, code snippets, etc.

[Django](djangoproject.com)

[Bootstrap 5](getbootstrap.com)

[MITRE ATT&CK Framework](attack.mitre.org)

[Google Font](fonts.google.com)

[Python Software Foundation](python.org)

[Claude (Anthropic)](https://claude.ai/share/840ab7ef-1b92-4dc3-bd62-c7ede5aaa7d9)