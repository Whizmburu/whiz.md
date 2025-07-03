# commands/owner/uptime_command.py
import time

async def handle_uptime(message, args, client, bot_instance):
    """
    Handles the /uptime command.
    Shows the bot's current uptime.
    """
    uptime_str = bot_instance.get_uptime()
    response_message = f"🤖 Bot Uptime: {uptime_str}"

    # await message.reply(response_message) # Placeholder
    print(f"Output for /uptime: {response_message}")

if __name__ == '__main__':
    import asyncio

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    class MockBotInstance:
        def __init__(self):
            self.start_time = time.time() - (3600 * 3 + 60 * 30) # 3 hours 30 minutes ago

        def get_uptime(self):
            uptime_seconds = time.time() - self.start_time
            days = int(uptime_seconds // (24 * 3600))
            uptime_seconds %= (24 * 3600)
            hours = int(uptime_seconds // 3600)
            uptime_seconds %= 3600
            minutes = int(uptime_seconds // 60)
            seconds = int(uptime_seconds % 60)
            if days > 0: return f"{days}d {hours}h {minutes}m {seconds}s"
            if hours > 0: return f"{hours}h {minutes}m {seconds}s"
            return f"{minutes}m {seconds}s"

    mock_msg = MockMessage()
    mock_bot = MockBotInstance()
    asyncio.run(handle_uptime(mock_msg, [], None, mock_bot))
