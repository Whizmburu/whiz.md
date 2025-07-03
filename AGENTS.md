# AGENTS.md - Instructions for AI Agents Working on WHIZ-MD Bot

Welcome, AI Agent! This document provides guidelines and context for working on the WHIZ-MD Bot codebase.

## 🎯 Project Goal

The primary goal is to develop a Python-based WhatsApp bot as per the specifications provided in `WHIZ-MD-BOT-SYSTEM-SPECIFICATION.md` (or the initial prompt if this file doesn't exist). This includes implementing various commands, ensuring proper configuration management, and maintaining a clean, modular codebase.

## 🔧 Development Environment

*   **Language:** Python (version 3.8+ preferred)
*   **Package Management:** Pip with `requirements.txt`. Ensure any new dependencies are added to `requirements.txt`.
*   **Environment Variables:** All sensitive data (API keys, session IDs, etc.) and core configurations must be managed via an `.env` file. A `.env.example` file should be maintained.
*   **WhatsApp Integration:** The choice of Python WhatsApp library is critical. Initial development might use placeholders. If a specific library is chosen, adhere to its API and best practices.

## 🏛️ Codebase Structure and Conventions

*   **Modularity:**
    *   Commands should be organized into subdirectories within the `commands/` directory, categorized as specified (e.g., `commands/owner`, `commands/utility`).
    *   Each command should ideally be in its own Python file (e.g., `commands/owner/ping.py`).
    *   Utility functions (config loading, logging, message templates) should be in the `utils/` directory.
*   **Naming:**
    *   Follow PEP 8 naming conventions for Python code (snake_case for functions and variables, PascalCase for classes).
    *   Command files should be named descriptively (e.g., `ping.py`, `sticker_command.py`).
*   **Asynchronous Operations:** WhatsApp communication is inherently asynchronous. Use `async` and `await` appropriately when interacting with the WhatsApp library. Command handlers will likely need to be asynchronous.
*   **Error Handling:** Implement robust error handling. Inform users gracefully if a command fails or input is invalid. Log errors for debugging.
*   **Logging:** Use the logger configured in `utils/logger.py`. Add informative log messages, especially for command execution, errors, and important lifecycle events (startup, connection, disconnection).
*   **Docstrings and Comments:**
    *   Write clear docstrings for all modules, classes, functions, and methods, explaining their purpose, arguments, and return values.
    *   Use comments to clarify complex or non-obvious code sections.
*   **Configuration Access:** Access configuration values (from `.env`) through the `Config` class in `utils/config.py`. Do not hardcode configurable values directly in command files.
*   **Message Templates:** Use the `MessageTemplates` class in `utils/message_templates.py` for generating standardized bot messages (connect, ping, menu, etc.).

## ✅ Key Requirements from Specification

*   **SESSION_ID Validation:** The `SESSION_ID` must start with `WHIZ_`. The bot should refuse to start or prompt the user if this condition is not met, guiding them to `https://whizmdsessions.onrender.com`. This is implemented in `utils/config.py` and checked in `whiz_md_bot.py`.
*   **Message Layouts:** Adhere to the specified message layouts for "Connected," "Ping," and "Main Menu." These are managed by `utils/message_templates.py`.
*   **Command Implementation:** Implement all 85 commands as listed in the specification. Each command should be placed in its appropriate category directory.
*   **`.env` File Usage:** All secrets and major configurations must be loaded from `.env`.
*   **Clickable Logo/Support Link:** The main menu should reference a clickable logo that links to the support group. The actual implementation of "clickable" depends on the WhatsApp library's capabilities (e.g., sending an image with a caption that includes a link, or using rich message formats if available). The link itself is `https://chat.whatsapp.com/JLmSbTfqf4I2Kh4SNJcWgM`.

## 🧪 Testing

*   While formal automated tests might not be part of the initial request, ensure that individual commands are testable.
*   Manually test commands after implementation to ensure they work as expected.
*   Consider how you might write unit tests for utility functions and command logic if requested later.

## 🔄 Workflow

1.  **Understand the Task:** Carefully read the user's request and the relevant parts of the system specification.
2.  **Plan:** Use the `set_plan` tool to outline your steps.
3.  **Implement:** Write code following the guidelines above.
    *   Create new files for commands as needed.
    *   Update existing files carefully.
4.  **Verify:**
    *   If you add new dependencies, mention that they should be added to `requirements.txt`. (Actually creating/updating `requirements.txt` can be a separate step).
    *   Read through your changes to catch errors.
    *   If possible, mentally simulate the execution flow.
5.  **Communicate:** Use `plan_step_complete` after each step. Use `message_user` for updates or questions.

## 🛑 Important Reminders

*   **Do not ask the user to install dependencies or run commands directly in their terminal.** You are responsible for managing the environment within the tool's capabilities (e.g., using `run_in_bash_session` if you were to actually execute the bot or install packages).
*   **Focus on Python:** The target is a Python bot. Ignore any existing JavaScript/Node.js files unless specifically asked to analyze or convert them.
*   **Placeholder for WhatsApp Client:** The actual WhatsApp client library is not yet defined. Your initial code will likely use placeholder calls for sending messages, receiving events, etc. Design the command handlers to be adaptable once a client library is chosen. For example, a command handler might take a `message` object and an `args` list, and then call a hypothetical `await message.reply("response")`.

By following these guidelines, you'll help create a robust and maintainable WHIZ-MD Bot. Good luck!
