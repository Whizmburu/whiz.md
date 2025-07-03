# commands/owner/report_command.py

async def handle_report(message, args, client, bot_instance):
    """
    Handles the /report command.
    Allows users to report bugs or issues.
    """
    if not args:
        response_message = (
            f"⚠️ Please provide a description of the bug or issue you want to report.\n"
            f"Example: `/report The /ping command is slow.`\n\n"
            f"Alternatively, you can join the support group: {bot_instance.config.support_group_link}"
        )
        # await message.reply(response_message) # Placeholder
        print(f"Output for /report (no args):\n{response_message}")
        return

    report_text = " ".join(args)
    user_who_reported = message.sender # This would be the user's identifier

    # In a real bot, this report might be:
    # 1. Sent to the bot owner via DM.
    # 2. Logged to a specific file or database.
    # 3. Sent to a dedicated support channel/group.

    owner_notification = (
        f"🐞 **New Bug Report from {user_who_reported}** 🐞\n\n"
        f"**Report:**\n{report_text}\n\n"
        f"Timestamp: {bot_instance.message_templates.get_connected_message().split('Timestamp  : ')[1].split('\\n')[0]}" # Bit hacky way to get time
    )

    # Simulate sending to owner (e.g., client.send_message(bot_instance.config.owner_id, owner_notification))
    print(f"--- SIMULATED REPORT TO OWNER ---\n{owner_notification}\n---------------------------------")

    response_to_user = (
        f"✅ Thank you for your report!\n\n"
        f"Your issue has been noted: \"_{report_text}_\"\n"
        f"The owner ({bot_instance.owner_name}) has been notified.\n"
        f"For urgent matters, consider joining the support group: {bot_instance.config.support_group_link}"
    )
    # await message.reply(response_to_user) # Placeholder
    print(f"Output for /report (to user):\n{response_to_user}")

if __name__ == '__main__':
    import asyncio
    from datetime import datetime # For message_templates in mock

    class MockMessage:
        def __init__(self, sender="User123"):
            self.sender = sender
        async def reply(self, text):
            print(f"BOT REPLIED TO {self.sender}: {text}")

    class MockConfig:
        def __init__(self):
            self.support_group_link = "https://example.com/support"
            # self.owner_id = "OwnerJID" # For actual notification

    class MockMessageTemplates: # Simplified for this test
         def get_connected_message(self): # To provide a timestamp
            return f"Timestamp  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    class MockBotInstance:
        def __init__(self):
            self.config = MockConfig()
            self.owner_name = "TestOwner"
            self.message_templates = MockMessageTemplates()


    mock_bot = MockBotInstance()

    async def test_report():
        print("--- Test 1: Report with arguments ---")
        await handle_report(MockMessage("BugReporter"), ["The", "/about", "command", "has", "a", "typo."], None, mock_bot)

        print("\n--- Test 2: Report without arguments ---")
        await handle_report(MockMessage("ConfusedUser"), [], None, mock_bot)

    asyncio.run(test_report())
