# 🤖 gollum-izle

A multipurpose Python bot.

## 📖 Context & Explanation

This is the first Discord bot I ever wrote in Python.

This codebase is *old* compared to *now*, and I only verified it by manually testing the commands when putting the code on GitHub. Thus, there may be bugs or inefficiencies hidden in plain sight.

Concerning *old* and *now*:

* **Now**: `2025-07-28`
* **Oldest recorded version**: `2023-01-11 14:48:20`
* **Version used as base**: `2023-06-26 16:12:55`

## ✨ Features

* `/mcping <address> [hidden]`: Shows information about a Minecraft server and includes a fun fact.

* `/randserver [count] [only_digits] [hidden]`: Returns a list of **online** Minecraft servers selected from the `./src/online-mc-servers.json` file. `[only_digits]` returns only servers with bare IPv4 addresses.

* `/latest <youtuber> [prior_to] [hidden]`: Shows the latest `[prior_to]` videos from the specified `<youtuber>`.

* `/export [format(txt,csv)]`: Exports the current text channel into a file.

*Arguments in angle brackets `<>` are mandatory.*
*Arguments in square brackets `[]` are optional.*
*The `[hidden]` boolean makes the response ephemeral (visible only to the command sender).*

## 🚀 Installation

### 🐳 Docker Compose (recommended)

1. Clone the repository and navigate into it:

```bash
git clone https://github.com/Urpagin/gollum-izle.git
cd gollum-izle
```

2. Copy the `.env.example` file to `.env` and populate it according to the instructions within.

3. Start the bot using Docker Compose:

```bash
sudo docker compose up -d
```

### 🐍 Python

1. Clone the repository and navigate into it:

```bash
git clone https://github.com/Urpagin/gollum-izle.git
cd gollum-izle
```

2. Copy the `.env.example` file to `.env` and populate it according to the instructions within.

3. Install dependencies (Python >=3.11, tested on 3.13):

```bash
pip install -r requirements.txt
```

4. Start the bot (ensure you are in the root directory):

```bash
python -m src.main
```

## 🛠️ To Fix / To Do

* Use temporary files instead of saving files directly to a tangible directory.
