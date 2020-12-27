# GriffinBot
A bot for the Roycemore Discord server.

[![Bitbucket open issues](https://img.shields.io/bitbucket/issues-raw/NinoMaruszewski/griffinbot?style=for-the-badge)](https://bitbucket.org/NinoMaruszewski/griffinbot/issues) [![Bitbucket open pull requests](https://img.shields.io/bitbucket/pr-raw/NinoMaruszewski/griffinbot?style=for-the-badge)](https://bitbucket.org/NinoMaruszewski/griffinbot/pull-requests) [![License](https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge)](./LICENSE)

## Table of Contents

- [About](#About)
- [Getting Started](#Getting-Started)
- [Usage](#usage)
- [Deployment](#deployment)
- [Built Using](#Built-Using)
- [Authors](#authors)
- [TODO](./TODO.md)
- [Contributing](./CONTRIBUTING.md)

## About

This is s a Discord bot for the Roycemore Discord server. It provides moderation tools and is a "serious bot" without many games.

## Getting Started

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

## Usage

Starting the bot:

```sh
pipenv run start
```

Linting:

```sh
pipenv run lint
```
## Deployment

You can use [PM2](https://pm2.keymetrics.io/) to deploy it. If you have a better solution, create an issue in the issue tracker.

## Built Using

- [Discord.py](https://discordpy.readthedocs.io/en/latest/) - Discord API interface
- [SQLite3](https://sqlite.org/index.html) - Database

## Authors

- [@NinoMaruszewski](https://bitbucket.org/NinoMaruszewski/) - Idea & Initial work
- [@AlemSnyder](https://github.com/AlemSnyder/) - Main work
