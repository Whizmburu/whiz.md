# commands/owner/about_command.py

async def handle_about(message, args, client, bot_instance):
    """
    Handles the /about command.
    Shows information about the bot.
    """
    # Assuming bot_instance has attributes like bot_name, owner_name, repo_url, etc.
    # These would ideally be loaded from config.

    bot_name = bot_instance.bot_name
    owner_name = bot_instance.owner_name
    repo_url = bot_instance.config.repo_url # Accessing via config object in bot_instance
    version = "1.0.0 (Python Edition)" # Example version

    response_message = (
        f"🤖 **About {bot_name}** 🤖\n\n"
        f"Hi there! I'm {bot_name}, a multi-purpose WhatsApp bot.\n"
        f"Developed with Python and lots of ☕.\n\n"
        f"👤 **Owner:** {owner_name}\n"
        f"🔧 **Version:** {version}\n"
        f"💻 **Source Code:** {repo_url}\n"
        f"💬 **Total Commands (Planned):** 85\n\n" # This could be dynamic later
        f"I'm here to help with various tasks, from utilities to fun commands. "
        f"Type `/help` or `/menu` to see what I can do!\n\n"
        f"Powered by WHIZ-MD Technology."
    )

    # await message.reply(response_message) # Placeholder
    print(f"Output for /about:\n{response_message}")

if __name__ == '__main__':
    import asyncio

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    class MockConfig:
        def __init__(self):
            self.repo_url = "github.com/WHIZ-MD/Bot-Python"

    class MockBotInstance:
        def __init__(self):
            self.bot_name = "TestBot-MD"
            self.owner_name = "TestWhiz"
            self.config = MockConfig()

    mock_msg = MockMessage()
    mock_bot = MockBotInstance()
    asyncio.run(handle_about(mock_msg, [], None, mock_bot))
