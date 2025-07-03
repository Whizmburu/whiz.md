# commands/owner/support_command.py

async def handle_support(message, args, client, bot_instance):
    """
    Handles the /support command.
    Provides a link to the WhatsApp support group.
    """
    support_group_link = bot_instance.config.support_group_link
    bot_name = bot_instance.bot_name
    owner_name = bot_instance.owner_name

    # The spec mentions a clickable logo in the main menu.
    # This command can reinforce that and provide the direct link.

    response_message = (
        f"📞 **{bot_name} Support Information** 📞\n\n"
        f"Need help or have questions? Join our official WhatsApp support group!\n\n"
        f"➡️  **Support Group Link:** {support_group_link}\n\n"
        f"In the group, you can:\n"
        f"- Ask questions about bot features.\n"
        f"- Report bugs or suggest new features.\n"
        f"- Get assistance from the community or {owner_name}.\n\n"
        f"We look forward to seeing you there! You can also find this link in the `/menu`."
    )

    # If the WhatsApp library allows sending messages with clickable links or rich previews,
    # that would be ideal here. For now, the text link is provided.

    # await message.reply(response_message) # Placeholder
    print(f"Output for /support:\n{response_message}")

if __name__ == '__main__':
    import asyncio

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    class MockConfig:
        def __init__(self):
            self.support_group_link = "https://chat.whatsapp.com/JLmSbTfqf4I2Kh4SNJcWgM"

    class MockBotInstance:
        def __init__(self):
            self.bot_name = "SupportiveBot"
            self.owner_name = "Whizzy"
            self.config = MockConfig()

    mock_msg = MockMessage()
    mock_bot = MockBotInstance()
    asyncio.run(handle_support(mock_msg, [], None, mock_bot))
