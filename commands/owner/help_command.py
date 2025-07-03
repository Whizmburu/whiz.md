# commands/owner/help_command.py

# This command will become more complex as we add more commands.
# For now, it can point to the /menu command or provide a basic message.

async def handle_help(message, args, client, bot_instance):
    """
    Handles the /help command.
    Provides help information, possibly linking to the menu or a command list.
    """
    # In a more advanced version, this could:
    # 1. List all commands.
    # 2. Provide help for a specific command if args are given (e.g., /help ping).
    # 3. Be dynamically generated from registered commands.

    command_categories = [
        "Owner ⚙️", "Utility 🛠️", "AI / Tools 🧐", "Group Admin 👮",
        "Media 🖼", "Fun 🎮", "Internet 🌐", "Downloaders 📀",
        "Text & Fonts 🎨", "Dev Tools 🚀"
    ]

    response_message = (
        f"🆘 **{bot_instance.bot_name} Help Center** 🆘\n\n"
        f"Hello! I'm {bot_instance.bot_name}. Here's how I can assist you:\n\n"
        f"➡️  Use `/menu` to see the full interactive menu.\n\n"
        f"I have commands in the following categories:\n"
    )
    for category in command_categories:
        response_message += f"  - {category}\n"

    response_message += (
        f"\n"
        f"You can explore these categories further via the `/menu` command. "
        f"In the future, you might be able to use `/help <command_name>` for specific command details.\n\n"
        f"For bug reports, use `/report <your_message>`.\n"
        f"For support, use `/support` to get our group link."
    )

    # await message.reply(response_message) # Placeholder for actual send
    print(f"Output for /help:\n{response_message}")

if __name__ == '__main__':
    import asyncio

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    class MockBotInstance:
        def __init__(self):
            self.bot_name = "HelperBot"

    mock_msg = MockMessage()
    mock_bot = MockBotInstance()
    asyncio.run(handle_help(mock_msg, [], None, mock_bot))
