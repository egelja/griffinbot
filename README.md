<p align="center">
  <a href="https://github.com/NinoMaruszewski/griffinbot" rel="noopener">
    <img width=200px height=200px src="https://cdn.pixabay.com/photo/2019/02/25/00/54/griffin-4018762_960_720.png">
  </a>
</p>

<h3 align="center">Griffin Bot</h3>

<div align="center">

[![GitHub issues](https://img.shields.io/github/issues/NinoMaruszewski/griffinbot?style=for-the-badge)](https://github.com/NinoMaruszewski/griffinbot/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/NinoMaruszewski/griffinbot?style=for-the-badge)](https://github.com/NinoMaruszewski/griffinbot/pulls)
[![GitHub](https://img.shields.io/github/license/NinoMaruszewski/griffinbot?style=for-the-badge)](./LICENSE)

</div>

---

<p align="center">
  A game bot for the Roycemore Discord server.
  <br>
</p>

## Table of Contents

- [About](#about)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Deployment](#deployment)
- [Built Using](#built-using)
- [Authors](#authors)
- [TODO](./TODO.md)
- [Contributing](./CONTRIBUTING.md)

## About <a name = "about"></a>

This is s a Discord bot for the Roycemore Discord server. It is a game bot made from submitted community bots.

## Getting Started <a name = "getting-started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

First install pipenv:

```sh
pip install pipenv
```

### Installing

Now install everything you need from the Pipfile. This will also create a virtual environment.

```sh
pipenv sync --dev
```

Now set up `pre-commit`:

```sh
pipenv run precommit
```

## Usage <a name = "usage"></a>

Starting the bot:

```sh
pipenv run start
```

Linting:

```sh
pipenv run lint
```

## Deployment <a name = "deployment"></a>

You can use [PM2](https://pm2.keymetrics.io/) to deploy it. If you have a better solution, create an issue in the issue tracker.

## Built Using <a name = "built-using"></a>

- [Discord.py](https://discordpy.readthedocs.io/en/latest/) - Discord API interface
- [SQLite3](https://sqlite.org/index.html) - Database

## Authors <a name = "authors"></a>

- [@NinoMaruszewski](https://github.com/NinoMaruszewski/) - Idea & Initial work
- [@AlemSnyder](https://github.com/AlemSnyder/) - Minesweeper
