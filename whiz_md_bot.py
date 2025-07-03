import os
import time
from datetime import datetime

from utils.config import Config
from utils.message_templates import MessageTemplates
# We'll need a logging setup later
# from utils.logger import setup_logger

# Placeholder for a WhatsApp client library, e.g., whatsapp-web.js wrapper or Baileys
# from whatsapp_client import WhatsAppClient # This is a hypothetical library

class WhizMdBot:
    def __init__(self):
        self.config = Config()
        # self.logger = setup_logger(__name__, self.config.log_level) # Example
        print("Initializing Whiz-MD Bot...")

        if not self.config.session_id or not self.config.session_id.startswith("WHIZ_"):
            print("🔴 FATAL ERROR: Invalid or missing SESSION_ID.")
            print(f"Please ensure your .env file has a valid SESSION_ID starting with 'WHIZ_'.")
            print(f"You can obtain a valid session ID from: {self.config.session_id_provider_url}")
            exit(1)

        self.bot_name = self.config.bot_name
        self.owner_name = self.config.owner_name
        self.start_time = time.time()
        self.message_templates = MessageTemplates(self.owner_name, self.bot_name) # Pass config details

        # Placeholder for actual WhatsApp client initialization
        # self.client = WhatsAppClient(session_id=self.config.session_id)
        # self.client.on_message(self.handle_message)
        # self.client.on_ready(self.on_ready)

        print(self.message_templates.get_connected_message())

    def on_ready(self):
        """Called when the bot is connected and ready."""
        # This is a placeholder. Actual implementation depends on the WhatsApp library.
        print(self.message_templates.get_connected_message())

    def get_uptime(self):
        """Calculates the bot's uptime."""
        uptime_seconds = time.time() - self.start_time
        days = int(uptime_seconds // (24 * 3600))
        uptime_seconds %= (24 * 3600)
        hours = int(uptime_seconds // 3600)
        uptime_seconds %= 3600
        minutes = int(uptime_seconds // 60)
        uptime_seconds %= 60
        seconds = int(uptime_seconds)

        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    async def handle_message(self, message):
        """
        Handles incoming messages.
        This is a placeholder and will need to be fleshed out with command parsing
        and calling the respective command handlers.
        """
        # print(f"Received message: {message.text} from {message.sender}") # Example

        # Basic command parsing example
        text = message.text.strip()
        # Assuming prefixes are stored in config or dynamically fetched
        prefixes = ["/", ".", "#", "whz", "!"] # Example, should come from config or be dynamic

        command_name = ""
        args = []

        for prefix in prefixes:
            if text.startswith(prefix):
                parts = text[len(prefix):].split()
                command_name = parts[0].lower()
                args = parts[1:]
                break

        if not command_name:
            return # Not a command

        # Command dispatching logic will go here
        # e.g., if command_name == "ping": await self.ping_command(message)
        #      elif command_name == "menu": await self.menu_command(message)

        if command_name == "ping":
            # Simulate sending a ping message
            # In a real bot, this would involve interaction with the WhatsApp client
            print(f"Executing ping command for {message.sender}")
            ping_time = "15" # Simulated
            load_avg = os.getloadavg()[0] # Example, might not be available on all OS
            uptime = self.get_uptime()
            ping_response = self.message_templates.get_ping_message(f"{ping_time}ms", uptime, f"{load_avg:.2f}")
            # await message.reply(ping_response) # Placeholder for sending reply
            print(ping_response) # For now, just print
            return

        if command_name == "menu":
            print(f"Executing menu command for {message.sender}")
            # These would be dynamic in a real bot
            num_commands = 85
            forks = 327
            uptime = self.get_uptime()
            current_prefixes = "/ . # whz !" # Example

            menu_response = self.message_templates.get_main_menu(
                owner=self.owner_name,
                repo_url="github.com/WHIZ-MD/Bot", # Should be from config
                prefixes=current_prefixes,
                forks=forks,
                command_count=num_commands,
                uptime=uptime,
                support_group_link="https://chat.whatsapp.com/JLmSbTfqf4I2Kh4SNJcWgM" # Should be from config
            )
            # await message.reply(menu_response) # Placeholder
            print(menu_response) # For now, just print
            return

        # Placeholder for other commands
        # print(f"Command '{command_name}' not yet implemented.")


    def run(self):
        """Starts the bot."""
        print(f"{self.bot_name} is starting...")
        # In a real scenario, this would start the WhatsApp client connection
        # self.client.connect()
        print(f"{self.bot_name} has started. Owner: {self.owner_name}")
        print("Simulating bot running. Press Ctrl+C to stop.")

        # Simulate keeping the bot alive.
        # In a real bot, this would be handled by the WhatsApp client's event loop.
        try:
            # Keep the main thread alive, or manage the event loop of the WhatsApp client
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down Whiz-MD Bot...")
        finally:
            # Perform any cleanup here
            # if self.client:
            #     self.client.disconnect()
            print("Whiz-MD Bot has been shut down.")

if __name__ == "__main__":
    bot = WhizMdBot()
    # bot.run() # We will run it once we have more pieces
    print("WhizMdBot initialized. Call bot.run() to start.")
    # For testing purposes, let's simulate a 'ready' event and some commands
    bot.on_ready()

    # Simulate receiving a ping command
    class MockMessage:
        def __init__(self, text, sender):
            self.text = text
            self.sender = sender
        async def reply(self, content): # Make reply async
            print(f"BOT REPLIED TO {self.sender}: {content}")

    import asyncio

    async def test_commands(): # Make test_commands async
        print("\n--- Simulating '/ping' command ---")
        await bot.handle_message(MockMessage("/ping", "TestUserPing"))

        print("\n--- Simulating '/menu' command ---")
        await bot.handle_message(MockMessage("/menu", "TestUserMenu"))

    # Run the async test function
    asyncio.run(test_commands())
    print("\n--- Main bot script execution finished ---")
    print("Next steps: Implement actual WhatsApp client integration and command handlers.")
