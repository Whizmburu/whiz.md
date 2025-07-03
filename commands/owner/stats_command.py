# commands/owner/stats_command.py
import psutil # Needs to be added to requirements.txt
import os

async def handle_stats(message, args, client, bot_instance):
    """
    Handles the /stats command.
    Shows CPU and memory usage.
    """
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory_info = psutil.virtual_memory()

    # Get process memory usage
    process = psutil.Process(os.getpid())
    process_memory_mb = process.memory_info().rss / (1024 * 1024) # RSS in MB

    response_message = (
        f"📊 Bot System Stats 📊\n"
        f"--------------------------\n"
        f"💻 CPU Usage: {cpu_usage}%\n"
        f"🧠 Total Memory: {memory_info.total / (1024**3):.2f} GB\n"
        f"📈 Used Memory: {memory_info.used / (1024**3):.2f} GB ({memory_info.percent}%)\n"
        f"📉 Free Memory: {memory_info.available / (1024**3):.2f} GB\n"
        f"🤖 Bot Memory Usage: {process_memory_mb:.2f} MB"
    )

    # await message.reply(response_message) # Placeholder
    print(f"Output for /stats:\n{response_message}")
    # Note: psutil needs to be added to requirements.txt

if __name__ == '__main__':
    import asyncio

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    # bot_instance isn't strictly needed for this command if it doesn't store state for it
    asyncio.run(handle_stats(MockMessage(), [], None, None))
    print("\nReminder: 'psutil' library is required for this command.")
