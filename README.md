<p align="center">
  <a href="https://github.com/MrAwesomeRocks/griffinbot" rel="noopener">
    <img width=200px height=200px src="https://cdn.pixabay.com/photo/2019/02/25/00/54/griffin-4018762_960_720.png">
  </a>
</p>

<h3 align="center">Griffin Bot</h3>

<div align="center">

[![GitHub issues](https://img.shields.io/github/issues/MrAwesomeRocks/griffinbot?style=for-the-badge)](https://github.com/MrAwesomeRocks/griffinbot/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/MrAwesomeRocks/griffinbot?style=for-the-badge)](https://github.com/MrAwesomeRocks/griffinbot/pulls)
[![GitHub](https://img.shields.io/github/license/MrAwesomeRocks/griffinbot?style=for-the-badge)](./LICENSE)

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

This is a Discord bot for the Roycemore Discord server. It is a game bot made from submitted community bots and games.

## Getting Started <a name = "getting-started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

First install [Python](https://python.org/), [Poetry](https://python-poetry.org/docs/#installation), and [Docker](https://www.docker.com/) from their websites.

### Installing

Now install everything you need using Poetry. This will also create a virtual environment.

```sh
poetry install
```

Now set up `pre-commit`:

```sh
poetry task run precommit
```

Now you should be able to do development on the bot! For more details on contributing, see the [Contributing](./CONTRIBUTING.md) file.

## Usage <a name = "usage"></a>

Starting the bot:

```sh
docker-compose up
```

Linting:

```sh
poetry task run lint
```

## Deployment <a name = "deployment"></a>

This bot is built using [Docker](https://www.docker.com/) and then deployed through the use of [remote docker-compose](https://www.docker.com/blog/how-to-deploy-on-remote-docker-hosts-with-docker-compose/).

## Built Using <a name = "built-using"></a>

- [Discord.py](https://discordpy.readthedocs.io/en/latest/) - Discord API interface
- [Uvloop](https://uvloop.readthedocs.io/) - Event loop
- [Flake8](https://flake8.pycqa.org/en/latest/) - Linting
- [Black](https://black.readthedocs.io/en/stable/) and [Isort](https://isort.readthedocs.io/en/latest/) - Formatting
- [Poetry](https://python-poetry.org) - Package manager
- [Docker](https://www.docker.com/) - Containerization and deployment

## Authors <a name = "authors"></a>

- [@MrAwesomeRocks](https://github.com/MrAwesomeRocks/) - Idea & Initial work
- [@AlemSnyder](https://github.com/AlemSnyder/) - Minesweeper
