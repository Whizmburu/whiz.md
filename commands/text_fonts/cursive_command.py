# commands/text_fonts/cursive_command.py
import asyncio
# Import the conversion function from fancy_command
# This requires fancy_command to be in the same directory or Python path accessible
try:
    from .fancy_command import convert_text_to_fancy, FANCY_STYLES
except ImportError:
    # Fallback if direct relative import fails (e.g. running script directly)
    # This indicates a potential issue with how modules are structured or run for testing
    # For bot operation, relative import should work if commands package is loaded correctly.
    print("Warning: Could not import from .fancy_command for /cursive. Cursive command might not work as expected if fancy_command.py is not found.")
    FANCY_STYLES = {} # Define as empty to prevent NameError later
    def convert_text_to_fancy(text, style): # Dummy function
        if "script" not in FANCY_STYLES:
             return "Cursive style data not loaded. Cannot convert."
        return "Error: Conversion function not loaded."


async def handle_cursive(message, args, client, bot_instance):
    """
    Handles the /cursive command.
    Converts text to a cursive Unicode style using the 'script' style
    from the fancy_command module.
    Usage: /cursive <text_to_convert>
    """
    command_name = "cursive"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply(f"Usage: /{command_name} <text to convert to cursive>")
        return

    text_to_convert = " ".join(args)

    # Check if the 'script' style is available from fancy_command
    if "script" not in FANCY_STYLES:
        error_msg = "Cursive text generation is currently unavailable (dependency missing or style not found)."
        print(error_msg)
        if hasattr(message, 'reply'): await message.reply(error_msg)
        return

    cursive_text = convert_text_to_fancy(text_to_convert, "script")

    if hasattr(message, 'reply'):
        await message.reply(cursive_text)
    else:
        print(f"Original: {text_to_convert}\nCursive: {cursive_text}")

if __name__ == '__main__':
    class MockMessage:
        def __init__(self, text, sender):
            self.text = text
            self.sender = sender
        async def reply(self, text_content):
            print(f"BOT REPLIED TO {self.sender}: {text_content}")

    class MockClient: pass
    class MockBotInstance: pass

    # To run this test directly, fancy_command.py must be in the python path
    # This usually means running from the project root with appropriate module paths.
    # For simplicity, if fancy_command's FANCY_STYLES can be accessed, this test will show output.
    # Otherwise, it will show the error message.

    async def main_test():
        mock_bot = MockBotInstance()
        mock_client = MockClient()

        print("\n--- Cursive Text Test Cases ---")

        # Need to ensure fancy_command's FANCY_STYLES is populated for tests
        # If FANCY_STYLES is empty due to import issues, these tests will reflect that.
        if "script" not in FANCY_STYLES:
            print("WARNING: FANCY_STYLES['script'] not loaded. Test results will be affected.")
            # Manually populate for test if needed, though this hides the import problem
            # FANCY_STYLES["script"] = {
            #    "normal": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
            #    "fancy": "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"
            # }
            # from commands.text_fonts.fancy_command import FANCY_STYLES as TestFancyStyles, convert_text_to_fancy as TestConvert
            # FANCY_STYLES.update(TestFancyStyles) # This is hacky for a direct script run
            # global convert_text_to_fancy
            # convert_text_to_fancy = TestConvert


        print("\nTest 1: Simple word")
        msg1 = MockMessage("/cursive Hello", "TestUserCursive_1")
        await handle_cursive(msg1, ["Hello"], mock_client, mock_bot)

        print("\nTest 2: Sentence with spaces")
        msg2 = MockMessage("/cursive Hello World 123", "TestUserCursive_2")
        await handle_cursive(msg2, ["Hello", "World", "123"], mock_client, mock_bot)

        print("\nTest 3: No arguments")
        msg3 = MockMessage("/cursive", "TestUserCursive_3")
        await handle_cursive(msg3, [], mock_client, mock_bot)

    asyncio.run(main_test())
