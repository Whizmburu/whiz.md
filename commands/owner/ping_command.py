# commands/owner/ping_command.py

# from utils.message_templates import MessageTemplates # Will be needed
# from main_bot_file import get_bot_instance # Or some way to access bot's uptime, load etc.
import time
import os # For os.getloadavg()

async def handle_ping(message, args, client, bot_instance):
    """
    Handles the /ping command.
    Measures response speed, shows uptime and system load.
    """
    # In a real scenario, 'client' would be the WhatsApp client instance
    # and 'bot_instance' our WhizMdBot instance.

    # 1. Calculate response time (this is simplified)
    # A more accurate ping would be to measure time to receive and process message.
    # For now, we'll simulate a processing delay.
    start_time = time.time()
    # Simulate some work
    await asyncio.sleep(0.01) # Placeholder for actual processing
    end_time = time.time()
    ping_duration_ms = round((end_time - start_time) * 1000)

    # 2. Get Uptime from bot_instance
    uptime_str = bot_instance.get_uptime() # Assuming get_uptime() is available

    # 3. Get Load Average
    try:
        load_avg = os.getloadavg()[0] # Gets 1-minute load average
        load_str = f"{load_avg:.2f}"
    except (AttributeError, IndexError, OSError): # os.getloadavg() not on Windows
        load_str = "N/A"

    # 4. Get message template
    # templates = MessageTemplates(bot_instance.owner_name, bot_instance.bot_name) # This might be better managed globally
    templates = bot_instance.message_templates

    response_message = templates.get_ping_message(
        ping_time=f"{ping_duration_ms}ms",
        uptime=uptime_str,
        load_avg=load_str
    )

    # await message.reply(response_message) # Placeholder for actual reply
    print(f"Output for /ping:\n{response_message}") # For now, print

# Example usage (for testing purposes, normally called by the bot's command dispatcher)
if __name__ == '__main__':
    import asyncio

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    class MockBotInstance:
        def __init__(self):
            self.start_time = time.time() - 3600 * 2 # Pretend bot started 2 hours ago
            self.owner_name = "TestOwner"
            self.bot_name = "TestBot"
            from utils.message_templates import MessageTemplates # Relative import for test
            self.message_templates = MessageTemplates(self.owner_name, self.bot_name)


        def get_uptime(self):
            uptime_seconds = time.time() - self.start_time
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    mock_msg = MockMessage()
    mock_bot = MockBotInstance()
    asyncio.run(handle_ping(mock_msg, [], None, mock_bot))
