import os
import time
from datetime import datetime
import asyncio # Added for asyncio.run and create_task
import traceback # For logging exception tracebacks

from utils.config import Config
from utils.message_templates import MessageTemplates
from utils.logger import setup_logger

# Import command handlers
from commands.owner import *
from commands.utility import *
from commands.ai_tools import *
from commands.group_admin import *
from commands.media import *
from commands.fun import *
from commands.internet import *
from commands.downloaders import *
from commands.text_fonts import *
from commands.dev_tools import *

# --- Hypothetical pybailey Library Mock Start ---
# The following classes (PyBaileyMessage, PyBaileyClient) are MOCKS for a
# hypothetical Python WhatsApp library wrapping Baileys (referred to as 'pybailey').
# They are used to simulate the structure and behavior of a real client library,
# allowing the bot's core logic (command dispatch, handlers) to be developed
# and tested without a live WhatsApp connection or a real, complex library setup.
# When integrating a REAL WhatsApp library, these mock classes would be REMOVED,
# and the actual library would be imported and used.

class PyBaileyClientEvent: # This class seems unused currently, can be removed or kept for future event types.
    """Hypothetical event object from pybailey (e.g., for status updates, group changes)."""
    def __init__(self, id, chat_id, sender_id, text, timestamp, is_group=False, replied_to_id=None, client_ref=None, bot_logger=None):
        self.id = id
        self.chat_id = chat_id
        self.sender_id = sender_id
        self.text = text
        self.timestamp = timestamp
        self.is_group = is_group
        self.replied_to_message_id = replied_to_id
        self._client_ref = client_ref # Reference to the pybailey client instance for actual sending
        self._logger = bot_logger if bot_logger else setup_logger('PyBaileyMessageMock', 'INFO')

    async def reply(self, text_content):
        if self._client_ref and hasattr(self._client_ref, 'send_text'):
            self._logger.info(f"Message {self.id} in {self.chat_id} is using its reply method.")
            await self._client_ref.send_text(self.chat_id, text_content, reply_to_message_id=self.id)
        else:
            self._logger.warning(f"PYBAILEY_MESSAGE_MOCK: Reply called on message {self.id} but no client_ref or send_text method found. Printing instead.")
            print(f"PYBAILEY_MESSAGE_MOCK (Print Fallback): Replying from message {self.id} in chat {self.chat_id} with: \"{text_content[:50]}...\"")

class PyBaileyClient: # Mocking the pybailey library's Client class
    """Hypothetical pybailey Client class."""
    def __init__(self, service_url, session_path, bot_logger):
        self._on_message_handler = None
        self._on_ready_handler = None
        self.is_connected = False
        self.service_url = service_url
        self.session_path = session_path
        self.logger = bot_logger # Use the bot's logger
        self.logger.info(f"PyBaileyClient initialized (mock). Service: {self.service_url}, Session: {self.session_path}")

    def on_message(self, func): # Called by WhizMdBot to register its message handler wrapper
        self.logger.info("PyBaileyClient_mock: WhizMdBot's on_message_wrapper registered.")
        self._on_message_handler = func

    def on_ready(self, func): # Called by WhizMdBot to register its ready handler wrapper
        self.logger.info("PyBaileyClient_mock: WhizMdBot's on_ready_wrapper registered.")
        self._on_ready_handler = func

    async def connect(self): # Called by WhizMdBot's run() method
        self.logger.info("PyBaileyClient_mock: connect() called. Simulating connection...")
        await asyncio.sleep(0.1) # Simulate network delay for connection
        self.is_connected = True
        self.logger.info("PyBaileyClient_mock: Successfully 'connected'.")
        if self._on_ready_handler:
            self.logger.info("PyBaileyClient_mock: Triggering on_ready handler.")
            await self._on_ready_handler() # Call WhizMdBot's _on_ready_wrapper

        # After connection, simulate receiving some messages to test the bot's dispatcher
        asyncio.create_task(self._simulate_incoming_messages_after_connect())

    async def _simulate_incoming_messages_after_connect(self):
        """Simulates the client receiving messages from WhatsApp after connection."""
        await asyncio.sleep(1) # Initial delay after 'ready'
        if self._on_message_handler:
            self.logger.info("PyBaileyClient_mock: Simulating first incoming message (/ping)...")
            # The PyBaileyMessage needs a reference to this client instance to use its send_text for replies.
            mock_raw_msg1 = PyBaileyMessage("msg_sim_1", "user1@chat", "user1@sender", "/ping", time.time(), client_ref=self, bot_logger=self.logger)
            await self._on_message_handler(mock_raw_msg1) # Calls WhizMdBot's _on_message_wrapper

            await asyncio.sleep(0.5)
            self.logger.info("PyBaileyClient_mock: Simulating second incoming message (.menu)...")
            mock_raw_msg2 = PyBaileyMessage("msg_sim_2", "user2@chat", "user2@sender", ".menu", time.time(), client_ref=self, bot_logger=self.logger)
            await self._on_message_handler(mock_raw_msg2)

            await asyncio.sleep(0.5)
            self.logger.info("PyBaileyClient_mock: Simulating third incoming message (/ask What is AI?)...")
            mock_raw_msg3 = PyBaileyMessage("msg_sim_3", "user1@chat", "user1@sender", "/ask What is AI?", time.time(), client_ref=self, bot_logger=self.logger)
            await self._on_message_handler(mock_raw_msg3)


    async def send_text(self, chat_id, text, reply_to_message_id=None, **kwargs):
        """Simulates sending a text message. Called by PyBaileyMessage.reply or directly."""
        reply_info = f" (replying to {reply_to_message_id})" if reply_to_message_id else ""
        self.logger.info(f"PYBAILEY_CLIENT_MOCK (send_text): To {chat_id}{reply_info}: \"{text[:100]}{'...' if len(text) > 100 else ''}\"")
        return {"id": f"sent_msg_{int(time.time())}"} # Simulate sent message object/ID

    async def send_image(self, chat_id, image_data_or_path, caption="", reply_to_message_id=None, **kwargs):
        """Simulates sending an image. Called by command handlers."""
        img_info = f"BytesIO (len {len(image_data_or_path.getvalue())})" if hasattr(image_data_or_path, 'getvalue') else str(image_data_or_path)
        reply_info = f" (replying to {reply_to_message_id})" if reply_to_message_id else ""
        self.logger.info(f"PYBAILEY_CLIENT_MOCK (send_image): To {chat_id}{reply_info}, Caption: \"{caption}\", Image: {img_info}")
        return {"id": f"sent_img_msg_{int(time.time())}"}

    async def send_video(self, chat_id, video_data_or_path, caption="", reply_to_message_id=None, **kwargs):
        """Simulates sending a video. Called by command handlers."""
        vid_info = f"BytesIO (len {len(video_data_or_path.getvalue())})" if hasattr(video_data_or_path, 'getvalue') else str(video_data_or_path)
        reply_info = f" (replying to {reply_to_message_id})" if reply_to_message_id else ""
        self.logger.info(f"PYBAILEY_CLIENT_MOCK (send_video): To {chat_id}{reply_info}, Caption: \"{caption}\", Video: {vid_info}")
        return {"id": f"sent_vid_msg_{int(time.time())}"}

    async def send_file(self, chat_id, file_data_or_path, caption="", filename="file", reply_to_message_id=None, **kwargs):
        """Simulates sending a file. Called by command handlers."""
        file_info = f"BytesIO (len {file_data_or_path.getvalue())})" if hasattr(file_data_or_path, 'getvalue') else str(file_data_or_path)
        reply_info = f" (replying to {reply_to_message_id})" if reply_to_message_id else ""
        self.logger.info(f"PYBAILEY_CLIENT_MOCK (send_file): To {chat_id}{reply_info}, File: '{filename}', Caption: \"{caption}\", Data: {file_info}")
        return {"id": f"sent_file_msg_{int(time.time())}"}
# --- End of Hypothetical pybailey Library Mock ---


class WhizMdBot:
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger('WhizMdBot', self.config.log_level)
        self.logger.info("Initializing Whiz-MD Bot...")

        if not self.config.session_id or not self.config.session_id.startswith("WHIZ_"):
            self.logger.error("🔴 FATAL ERROR: Invalid or missing SESSION_ID.")
            self.logger.error(f"Please ensure .env has a valid SESSION_ID starting with 'WHIZ_'.")
            self.logger.error(f"Get session ID from: {self.config.session_id_provider_url}")
            exit(1)

        self.bot_name = self.config.bot_name
        self.owner_name = self.config.owner_name
        self.start_time = time.time()
        self.message_templates = MessageTemplates(self.owner_name, self.bot_name)

        # Initialize the WhatsApp client (using the mock PyBaileyClient for now)
        # This client instance will be used by command handlers to send messages, files, etc.
        # and by the bot to register event listeners (on_message, on_ready).
        # When a real library is chosen, this instantiation will change.
        self.client = PyBaileyClient(
            service_url=self.config.whatsapp_client_service_url,
            session_path=self.config.whatsapp_session_path,
            bot_logger=self.logger # Pass bot's logger to the client mock for unified logging
        )

        self._register_commands()
        self.group_settings = {} # For features like /antilink

        # Register event handler wrappers with the (mocked) client instance.
        # In a real library, this is how the bot subscribes to events like new messages or successful connection.
        # The wrapper methods (_on_message_wrapper, _on_ready_wrapper) adapt the client library's
        # event format/data to what the WhizMdBot's internal methods (handle_message, on_ready) expect.
        self.client.on_message(self._on_message_wrapper)
        self.client.on_ready(self._on_ready_wrapper)

        self.logger.info(self.message_templates.get_connected_message().strip())
        self.logger.info(f"Total commands loaded: {len(self.commands)}")
        self.logger.info("WhizMdBot initialized. Call run() to connect and start listening.")

    def _register_commands(self):
        self.commands = {
            "ping": handle_ping, "uptime": handle_uptime, "stats": handle_stats,
            "about": handle_about, "help": handle_help, "prefix": handle_prefix,
            "setprefix": handle_setprefix, "report": handle_report,
            "invite": handle_invite, "support": handle_support,
            "calc": handle_calc, "qr": handle_qr, "translate": handle_translate,
            "shorturl": handle_shorturl, "weather": handle_weather, "time": handle_time,
            "reminder": handle_reminder, "timer": handle_timer,
            "dictionary": handle_dictionary, "quote": handle_quote,
            "ask": handle_ask, "imagegen": handle_imagegen, "summarize": handle_summarize,
            "codegen": handle_codegen, "chat": handle_chat,
            "ban": handle_ban, "kick": handle_kick, "mute": handle_mute,
            "warn": handle_warn, "unban": handle_unban, "promote": handle_promote,
            "demote": handle_demote, "groupinfo": handle_groupinfo,
            "antilink": handle_antilink, "lockgroup": handle_lockgroup,
            "sticker": handle_sticker, "toimg": handle_toimg, "tomp3": handle_tomp3,
            "gifsticker": handle_gifsticker, "removebg": handle_removebg,
            "resize": handle_resize, "filter": handle_filter, "vv": handle_vv,
            "joke": handle_joke, "meme": handle_meme, "8ball": handle_8ball,
            "truth": handle_truth, "dare": handle_dare, "ship": handle_ship,
            "rate": handle_rate, "rps": handle_rps, "coinflip": handle_coinflip,
            "guess": handle_guess,
            "news": handle_news, "wiki": handle_wiki, "movie": handle_movie,
            "anime": handle_anime, "github": handle_github, "npm": handle_npm,
            "ytmp3": handle_ytmp3, "ytmp4": handle_ytmp4, "igdl": handle_igdl,
            "tiktok": handle_tiktok, "fb": handle_fb, "twitter": handle_twitter,
            "mediafire": handle_mediafire, "apk": handle_apk,
            "fancy": handle_fancy, "ascii": handle_ascii, "emoji": handle_emoji,
            "reverse": handle_reverse, "zalgo": handle_zalgo,
            "cursive": handle_cursive, "tinytext": handle_tinytext,
            "base64": handle_base64, "jsonfmt": handle_jsonfmt, "whois": handle_whois,
            "dns": handle_dns, "headers": handle_headers,
        }
        self.commands["menu"] = self.display_main_menu

    async def _on_ready_wrapper(self):
        """Wrapper for the client's 'ready' event. Calls the bot's on_ready method."""
        self.logger.debug("Client 'ready' event received, calling bot.on_ready().")
        self.on_ready()

    async def _on_message_wrapper(self, lib_message_object: PyBaileyMessage):
        """
        Wrapper for the client's 'message' event.
        This crucial function adapts the message object from the specific WhatsApp library
        (here, our mock `PyBaileyMessage`) into a standardized format or ensures it's
        compatible with what `self.handle_message` and subsequent command handlers expect.
        A real library might provide a much more complex message object.
        """
        self.logger.debug(f"Received raw message event from client: ID {lib_message_object.id}, Sender {lib_message_object.sender_id}")

        # In this mock, PyBaileyMessage is already designed to be somewhat compatible
        # and its `reply` method uses the client instance passed to it during its creation.
        # For a real library, you might extract data into a new, simpler internal message object:
        # internal_message = {
        #     'text': lib_message_object.text,
        #     'sender': lib_message_object.sender_id, # Standardized field name
        #     'chat_id': lib_message_object.chat_id,
        #     'id': lib_message_object.id,
        #     'is_group': lib_message_object.is_group,
        #     'group_id': lib_message_object.chat_id if lib_message_object.is_group else None,
        #     'replied_to_message_id': lib_message_object.replied_to_id,
        #     'is_sender_admin': False, # This would need to be determined by the real library
        #     'mock_replied_message_details': None, # For /vv testing; real lib handles this
        #     # The reply method needs to be carefully bound or passed through.
        #     # Using the library's message object directly (if it has a reply method) is often easier.
        #     'reply': lambda text_content: self.client.send_text(
        #         lib_message_object.chat_id, text_content, reply_to_message_id=lib_message_object.id
        #     )
        # }
        # # Create a dynamic object or a dedicated class instance for internal_message
        # class StandardizedBotMessage:
        #     def __init__(self, **kwargs): self.__dict__.update(kwargs)
        # adapted_msg_obj = StandardizedBotMessage(**internal_message)
        # await self.handle_message(adapted_msg_obj)

        # For now, directly passing the PyBaileyMessage mock, as its .reply() is set up.
        # Command handlers will need to use .sender_id for sender, .chat_id for chat context.
        await self.handle_message(lib_message_object)


    async def display_main_menu(self, message, args, client, bot_instance):
        self.logger.info(f"Executing menu command for {message.sender_id if hasattr(message, 'sender_id') else message.sender}")
        num_commands = len(self.commands)
        forks = 327
        uptime = self.get_uptime()
        current_prefixes_str = " | ".join(self.config.prefixes)

        menu_response = self.message_templates.get_main_menu(
            owner=self.owner_name,
            repo_url=self.config.repo_url,
            prefixes=current_prefixes_str,
            forks=forks,
            command_count=num_commands,
            uptime=uptime,
            support_group_link=self.config.support_group_link
        )
        await message.reply(menu_response) # Uses the message object's own reply method


    def on_ready(self):
        self.logger.info("Bot is ready (on_ready event triggered).")
        self.logger.info(self.message_templates.get_connected_message().strip())

    def get_uptime(self):
        uptime_seconds = time.time() - self.start_time
        days = int(uptime_seconds // (24 * 3600)); uptime_seconds %= (24 * 3600)
        hours = int(uptime_seconds // 3600); uptime_seconds %= 3600
        minutes = int(uptime_seconds // 60); seconds = int(uptime_seconds % 60)
        if days > 0: return f"{days}d {hours}h {minutes}m {seconds}s"
        if hours > 0: return f"{hours}h {minutes}m {seconds}s"
        return f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"

    async def handle_message(self, message: PyBaileyMessage): # Now expects PyBaileyMessage type
        self.logger.debug(f"Handling message: '{message.text}' from {message.sender_id} in chat {message.chat_id}")
        text = message.text.strip()
        current_prefixes = self.config.prefixes
        parsed_command_name = None
        args = []

        for prefix in current_prefixes:
            if text.startswith(prefix):
                if len(text) > len(prefix):
                    command_body = text[len(prefix):]
                    parts = command_body.split()
                    if parts:
                        parsed_command_name = parts[0].lower()
                        args = parts[1:]
                break

        if not parsed_command_name:
            return

        command_handler = self.commands.get(parsed_command_name)
        if command_handler:
            self.logger.info(f"Executing command '{parsed_command_name}' for {message.sender_id} with args: {args}")
            try:
                # Command handlers expect (message, args, client, bot_instance)
                # client is self.client (the PyBaileyClient mock)
                # bot_instance is self (this WhizMdBot instance)
                await command_handler(message, args, self.client, self)
            except Exception as e:
                self.logger.error(f"🔴 ERROR executing command '{parsed_command_name}': {e}", exc_info=True)
                if hasattr(message, 'reply'):
                    await message.reply(f"⚠️ Error running `{parsed_command_name}`. Try again or report.")
        else:
            self.logger.debug(f"Command '{parsed_command_name}' not found for input: '{text}'")


    async def run(self): # Changed to async
        """Connects the WhatsApp client and keeps the bot running."""
        self.logger.info(f"{self.bot_name} run() method called. Attempting to connect client...")
        try:
            # The client.connect() should ideally be a blocking call or manage its own event loop
            # for receiving messages. For our mock, it connects, simulates messages, and then this run() might end.
            # A real bot would loop here indefinitely or be event-driven by the client library.
            await self.client.connect()

            self.logger.info(f"{self.bot_name} client connected (mock). Bot is 'running'.")
            self.logger.info("Mock client will simulate a few incoming messages now.")
            self.logger.info("In a real application, this would run indefinitely, listening for events.")

            # Keep the main task alive while the mock client simulates messages in background tasks.
            # This loop is primarily for the mock scenario to prevent premature exit.
            # A real client library might handle its own persistent connection and event loop.
            keep_alive_duration = 10 # seconds, for mock client to finish its simulated messages
            end_time = time.time() + keep_alive_duration
            while time.time() < end_time:
                if not self.client.is_connected: # Hypothetical check
                    self.logger.warning("Mock client reported disconnection. Exiting run loop.")
                    break
                await asyncio.sleep(1)
            self.logger.info("Mock run loop duration ended or client disconnected.")

        except KeyboardInterrupt:
            self.logger.info("\nShutting down Whiz-MD Bot via KeyboardInterrupt in run()...")
        except Exception as e:
            self.logger.error(f"Exception in WhizMdBot.run(): {e}", exc_info=True)
        finally:
            self.logger.info("WhizMdBot run() method finished.")
            # Perform any client cleanup if needed (e.g., await self.client.disconnect())


if __name__ == "__main__":
    # This is the main entry point when the script is executed.
    bot = WhizMdBot() # Initializes config, logger, client (mock), and registers commands.

    # The bot.run() method now handles connecting the client and (for the mock)
    # simulating some activity.
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        # This catch might be redundant if bot.run() also catches it, but good for safety.
        bot.logger.info("Application terminated by user (KeyboardInterrupt in __main__).")
    except Exception as e:
        # Catch any other unexpected errors during startup or the main run loop.
        bot.logger.error(f"Unhandled critical exception in __main__: {e}", exc_info=True)
    finally:
        # This will be logged after bot.run() completes or if an error occurs.
        bot.logger.info("\n--- Whiz-MD Bot main execution loop has concluded. ---")
