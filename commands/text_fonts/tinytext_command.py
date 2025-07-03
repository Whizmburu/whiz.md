# commands/text_fonts/tinytext_command.py
import asyncio
try:
    from .fancy_command import convert_text_to_fancy, FANCY_STYLES
except ImportError:
    print("Warning: Could not import from .fancy_command for /tinytext. Command might not work as expected.")
    FANCY_STYLES = {}
    def convert_text_to_fancy(text, style):
        if "smallcaps" not in FANCY_STYLES: # Check specific style
            return "Smallcaps style data not loaded. Cannot convert."
        return "Error: Conversion function not loaded."

async def handle_tinytext(message, args, client, bot_instance):
    """
    Handles the /tinytext command.
    Converts text to a small caps Unicode style using the 'smallcaps' style
    from the fancy_command module.
    Usage: /tinytext <text_to_convert>
    """
    command_name = "tinytext"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply(f"Usage: /{command_name} <text to convert to tiny text/smallcaps>")
        return

    text_to_convert = " ".join(args)

    if "smallcaps" not in FANCY_STYLES:
        error_msg = "Tiny text (smallcaps) generation is currently unavailable (dependency missing or style not found)."
        print(error_msg)
        if hasattr(message, 'reply'): await message.reply(error_msg)
        return

    tiny_text = convert_text_to_fancy(text_to_convert, "smallcaps")

    if hasattr(message, 'reply'):
        await message.reply(tiny_text)
    else:
        print(f"Original: {text_to_convert}\nTiny Text (Smallcaps): {tiny_text}")

if __name__ == '__main__':
    class MockMessage:
        def __init__(self, text, sender):
            self.text = text
            self.sender = sender
        async def reply(self, text_content):
            print(f"BOT REPLIED TO {self.sender}: {text_content}")

    class MockClient: pass
    class MockBotInstance: pass

    # For this test to run correctly standalone, fancy_command.py and its FANCY_STYLES
    # (including the "smallcaps" key) must be accessible.
    async def main_test():
        mock_bot = MockBotInstance()
        mock_client = MockClient()

        print("\n--- Tiny Text (Smallcaps) Test Cases ---")

        if "smallcaps" not in FANCY_STYLES:
            print("WARNING: FANCY_STYLES['smallcaps'] not loaded. Test results will be affected.")
            # To force test, one could manually insert the style here for the test scope
            # FANCY_STYLES["smallcaps"] = {
            #    "normal": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            #    "fancy":  "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ0123456789"
            # }
            # from commands.text_fonts.fancy_command import FANCY_STYLES as TestFancyStyles, convert_text_to_fancy as TestConvert
            # FANCY_STYLES.update(TestFancyStyles)
            # global convert_text_to_fancy
            # convert_text_to_fancy = TestConvert


        print("\nTest 1: Simple word (lowercase)")
        msg1 = MockMessage("/tinytext hello", "TestUserTiny_1")
        await handle_tinytext(msg1, ["hello"], mock_client, mock_bot)

        print("\nTest 2: Sentence with mixed case and numbers")
        msg2 = MockMessage("/tinytext Hello World 123", "TestUserTiny_2")
        await handle_tinytext(msg2, ["Hello", "World", "123"], mock_client, mock_bot)

        print("\nTest 3: All caps input")
        msg3 = MockMessage("/tinytext TESTING", "TestUserTiny_3")
        await handle_tinytext(msg3, ["TESTING"], mock_client, mock_bot)

        print("\nTest 4: No arguments")
        msg4 = MockMessage("/tinytext", "TestUserTiny_4")
        await handle_tinytext(msg4, [], mock_client, mock_bot)

        print("\nTest 5: Special characters (should mostly remain unchanged)")
        msg5 = MockMessage("/tinytext Test!@# String", "TestUserTiny_5")
        await handle_tinytext(msg5, ["Test!@#", "String"], mock_client, mock_bot)


    asyncio.run(main_test())
