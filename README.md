# Film Search Bot

Python project for searching films in a Sakila-style MySQL database with an optional Telegram bot interface.

## Features

- Search films by title
- Search films by genre and year
- Store query logs
- Telegram bot interface

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` from `.env.example` and fill local database credentials:

```bash
cp .env.example .env
```

Run console app:

```bash
python main.py
```

Run Telegram bot:

```bash
python bot.py
```

## Security

Do not commit `.env`, database passwords, Telegram bot tokens, logs, or IDE files.
