# Project game_bot

[![Build Status](https://github.com/zimkaa/game_bot/actions/workflows/checks.yaml/badge.svg?branch=main)](https://github.com/zimkaa/game_bot/actions/workflows/checks.yaml)

## Installation

1. git clone <https://github.com/zimkaa/game_bot.git>
2. cd game_bot
3. python -m venv .venv
4. pip install -r requirements.txt

```sh
git clone https://github.com/zimkaa/game_bot.git
cd game_bot
python -m venv .venv
pip install -r requirements.txt
```

## Get started

1. Create a .env file and write down the variables.
2. Required. Example:

    ```env
    LOGIN = "Example_login"
    PASSWORD = "Example_pass"
    ```

3. Optional. Example:

    ```env
    PROXY_IP = "0.0.0.0"
    PROXY_LOGIN = "Example_proxy_login"
    PROXY_PASS = "Example_proxy_pass"
    PROXY_PORT = 0000

    TG_TOKEN = "your_TG_BOT_token"
    CHANNEL_ID = "your_TG_ID_for_send_messages"
    ```

4. Correct the `local_config.py` file
5. Start

    ```sh
    python start.py
    ```
