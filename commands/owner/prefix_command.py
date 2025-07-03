# commands/owner/prefix_command.py

async def handle_prefix(message, args, client, bot_instance):
    """
    Handles the /prefix command.
    Displays the current prefixes the bot responds to.
    """
    # Prefixes are stored in the config object within bot_instance
    current_prefixes = " | ".join(bot_instance.config.prefixes)

    response_message = (
        f"🔤 **Current Bot Prefixes** 🔤\n\n"
        f"I respond to commands starting with any of the following prefixes:\n"
        f"➡️  `{current_prefixes}`\n\n"
        f"For example: `{bot_instance.config.prefixes[0]}ping` or `{bot_instance.config.prefixes[0]}menu`.\n\n"
        f"To change prefixes, admins can use the `/setprefix` command (if implemented and authorized)."
    )

    # await message.reply(response_message) # Placeholder
    print(f"Output for /prefix:\n{response_message}")

if __name__ == '__main__':
    import asyncio

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    class MockConfig:
        def __init__(self):
            self.prefixes = ["/", ".", "#", "whz", "!"]

    class MockBotInstance:
        def __init__(self):
            self.config = MockConfig()
            self.bot_name = "PrefixBot" # Not used in this command directly but good for context

    mock_msg = MockMessage()
    mock_bot = MockBotInstance()
    asyncio.run(handle_prefix(mock_msg, [], None, mock_bot))
