# WHIZ-MD Bot - Python Edition

WHIZ-MD is a feature-rich WhatsApp bot built with Python, designed to provide a wide array of functionalities including utilities, media tools, AI interactions, group management, and more, as specified in the initial WHIZ-MD Bot System Specification.

This Python version aims to implement the features and user experience detailed for the WHIZ-MD system.

## Features Overview

The bot includes a comprehensive set of commands (currently 79 implemented + menu) across various categories:
*   **Owner Commands:** Bot control and information (`/ping`, `/uptime`, `/stats`, `/about`, `/help`, `/prefix`, `/setprefix`, `/report`, `/invite`, `/support`).
*   **Utility Commands:** Everyday tools (`/calc`, `/qr`, `/translate`, `/shorturl`, `/weather`, `/time`, `/reminder`, `/timer`, `/dictionary`, `/quote`).
*   **AI / Tools:** Powered by OpenAI (`/ask`, `/imagegen` with DALL-E, `/summarize`, `/codegen`, `/chat` with session history).
*   **Group Admin Commands:** Group management tools (`/ban`, `/kick`, etc. - require admin privileges and actual WhatsApp library integration for full effect).
*   **Media Commands:** Sticker creation, image manipulation, view-once handling (`/sticker`, `/toimg`, `/vv`, etc. - many are placeholders pending media library choices and WhatsApp lib integration).
*   **Fun Commands:** Entertainment and games (`/joke`, `/meme`, `/8ball`, etc. - mostly placeholders).
*   **Internet Commands:** Information retrieval (`/news`, `/wiki`, `/movie`, etc. - mostly placeholders).
*   **Downloaders:** Media downloaders for various platforms (`/ytmp3`, `/ytmp4`, `/igdl`, `/tiktok`, `/fb`, `/twitter`, `/mediafire`. `/apk` is a safety-conscious placeholder).
*   **Text & Fonts:** Text manipulation tools (`/fancy`, `/ascii`, `/emoji`, `/reverse`, `/zalgo`, `/cursive`, `/tinytext`).
*   **Dev Tools:** Developer utilities (`/base64`, `/jsonfmt`, `/whois`, `/dns`, `/headers`).

For a detailed command list and descriptions, please refer to the original system specification or use the `/menu` and `/help` commands once the bot is running with a compatible WhatsApp client.

## Prerequisites

*   Python (3.8 or higher recommended).
*   Pip (Python package installer).
*   Git (for cloning the repository).
*   An active WhatsApp account.
*   **(For full operation with a real WhatsApp client)**: A chosen Python WhatsApp library and its dependencies (which might include Node.js, a web browser like Chromium, etc., depending on the library). See "WhatsApp Client Integration" below.

## Setup and Running (Current Development State)

1.  **Clone the Repository:**
    ```bash
    # Replace with the actual repository URL when available
    git clone https://github.com/your-username/whiz-md-bot-python.git
    cd whiz-md-bot-python
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This will install all Python libraries listed in `requirements.txt`, including `python-dotenv`, `openai`, `requests`, `yt-dlp`, various utility libraries, and a placeholder for a WhatsApp client (`pybailey` in the current mock).

4.  **Configure Environment Variables (`.env` file):**
    *   Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and fill in your actual values. Key variables include:
        *   `SESSION_ID`: Your WhatsApp session ID (must start with `WHIZ_`). Get from [https://whizmdsessions.onrender.com](https://whizmdsessions.onrender.com).
        *   `BOT_NAME`: Your bot's name.
        *   `OWNER_NAME`: Your name (as the bot owner).
        *   `OWNER_JID`: Your WhatsApp JID (e.g., `yournumber@s.whatsapp.net`), used for owner-only commands like `/setprefix`.
        *   `OPENAI_API_KEY`: Your OpenAI API key for AI features (`/ask`, `/imagegen`, etc.).
        *   `OPENWEATHERMAP_API_KEY`: For the `/weather` command.
        *   `BOT_WHATSAPP_NUMBER`: The bot's WhatsApp number (for the `/invite` command).
        *   Other settings like `PREFIXES`, `LOG_LEVEL`, `SUPPORT_GROUP_LINK`, etc.

5.  **Running the Bot (with Mocked WhatsApp Client):**
    The current `whiz_md_bot.py` includes a **mocked** WhatsApp client (`PyBaileyClient`). This allows testing the bot's command handling and core logic without connecting to WhatsApp.
    ```bash
    python whiz_md_bot.py
    ```
    The script will initialize the bot, and the mock client will simulate receiving a few test messages (like `/ping`, `/menu`) which you'll see processed in the console logs.

## WhatsApp Client Integration (Important!)

The bot is currently developed with a **mocked WhatsApp client** (`PyBaileyClient` defined within `whiz_md_bot.py`). This is for development and testing of the bot's features *independent of a live WhatsApp connection*.

**To make this bot actually connect to WhatsApp and interact, you will need to:**

1.  **Choose a Python WhatsApp Library:**
    *   Research and select a suitable Python library that wraps a WhatsApp Web API (like Baileys or whatsapp-web.js). Examples of such wrappers vary in stability and maintenance. The user previously indicated a preference for a Baileys-based wrapper.
    *   **Note:** These libraries often have their own complex dependencies (e.g., Node.js, specific browser versions if they use Puppeteer/Selenium).

2.  **Integrate the Chosen Library:**
    *   Install the library and its dependencies.
    *   **Replace the mock `PyBaileyClient` and `PyBaileyMessage` classes in `whiz_md_bot.py` with the actual client and message objects from your chosen library.**
    *   Adapt the client initialization in `WhizMdBot.__init__()`.
    *   Adapt the event handling:
        *   `_on_ready_wrapper`: Connect to the library's "ready/connected" event.
        *   `_on_message_wrapper`: Connect to the library's "new message" event. You will need to adapt the incoming message object from the library to a structure that `handle_message` and your command handlers can use (or modify handlers to use the library's message object directly). This includes how `message.text`, `message.sender`, `message.chat_id`, `message.reply()`, etc., are accessed and used.
    *   Adapt sending methods: Update how text, images, videos, and files are sent in command handlers to use the methods provided by your chosen library (e.g., `client.send_text()`, `client.send_image()`).

3.  **Session Management:**
    *   Handle WhatsApp session setup for the chosen library (usually involves scanning a QR code from your phone). The library will typically save session data to a specified path (e.g., configured via `WHATSAPP_SESSION_PATH` in `.env`).

This integration is a significant step and requires careful attention to the chosen library's documentation and API.

## Code Structure

*   `whiz_md_bot.py`: Main bot script, includes `WhizMdBot` class, command dispatcher, and (currently) the mock WhatsApp client.
*   `utils/`: Utility modules:
    *   `config.py`: Loads configuration from `.env`.
    *   `logger.py`: Sets up logging.
    *   `message_templates.py`: Generates standardized bot messages (menu, ping, connect).
*   `commands/`: Contains subdirectories for different command categories (e.g., `owner`, `utility`, `ai_tools`). Each command is in its own file.
    *   `commands/category/__init__.py`: Imports all handlers from that category.
*   `features/`: For non-command-based features (e.g., `status_handler.py` placeholder).
*   `requirements.txt`: Python dependencies.
*   `.env.example`: Template for environment variables.
*   `AGENTS.md`: Instructions for AI agents working on this codebase.

## Contributing

If you are an AI agent working on this code, please refer to `AGENTS.md` for specific guidelines. For human contributors, standard GitHub practices (fork, branch, PR) apply.

---

Maintained by **WHIZ** (as per original specification).
This Python version developed by Jules (AI Agent).
