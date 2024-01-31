# HH.ru Vacancy Parser

Parse vacancies from [hh.ru](https://hh.ru/) to local database according to specified criteria (search phrase, city, employment, etc.).

Uses: Python 3.11, Flask, SQLite, Docker, [HeadHunter API](https://dev.hh.ru/).

## Installation

### Local Linux machine with Python 3.11 and Git

- install Git (<https://git-scm.com/downloads>)
- clone GitHub repository

  `git clone https://github.com/ilavir/hh_parser.git`

- inside project directory make a virtual environment

  `python3 -m venv .venv`

- activate virtual environment and install dependencies

  `source .venv/bin/activate`

  `pip install -r requirements.txt`

- rename *.env.example* to *.env* and specify hh.ru API tokens in *.env* file
- run Flask frontend on <http://localhost:8000>

  `flask run`

### Local machine with Docker Engine and Git

- install Git (<https://git-scm.com/downloads>)
- clone GitHub repository

  `git clone https://github.com/ilavir/hh_parser.git`
- rename *.env.example* to *.env* and specify hh.ru API tokens in *.env* file
- install Docker Engine (<https://docs.docker.com/engine/install/>)
- start services with Docker Compose

  `docker compose up --build`

### Local machine with Docker Engine

- download *.env.example* and *compose.yaml* from repository
- rename *.env.example* to *.env* and specify hh.ru API tokens in *.env* file
- install Docker Engine (<https://docs.docker.com/engine/install/>)
- start services with Docker Compose

  `docker compose up`

## Usage

### Docker Container

- check if the **hh-parser** service is started

  `docker ps`

- if the service is not started, start the service

  `docker compose up`

- to create a local database and search for vacancies on [hh.ru](https://hh.ru), run

  `docker exec -it hh-parser-web-1 ./crawler/crawler.py -d -e`

- to view and manage vacancies, open <http://localhost:8000> in a browser

### Flask server

- to create a local database and search for vacancies on [hh.ru](https://hh.ru), run

  `./crawler/crawler.py -d -e`

- to view and manage vacancies, open <http://localhost:8000> in a browser
