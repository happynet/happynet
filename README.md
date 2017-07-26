# Network Application

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)
![coverage](https://img.shields.io/badge/coverage-0%25-red.svg)

## Project for Python 300 course, part of UW PCE Python Programming certificate.

## Team: Ashay Krishna, Jing Dai, Mike Bozee

![project interface screenshot](documentation/py300-project-screenshot-jul26.png)

## Instruction to run locally:

- Clone this repo
- Activate project virtualenv, "py300_project":
```
$ source py300_project/bin/activate
```
- Run server:
```
$ cd network_site
$ python manage.py runserver
```
- View in browser at http://localhost:8000/

## Mike's Todo:

- [x] Ability to log in through GitHub/Google via allauth
- [ ] Ability to log out of allauth account(s)
- [ ] Deploy to [AWS Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/)
- [ ] Ability to manage site account
- [x] Incorporate mock-up UI from https://github.com/mikebozee/py300-network-project
- [ ] Connect to GNS3 virtual networks
- [ ] Assess and manage sqlite db
