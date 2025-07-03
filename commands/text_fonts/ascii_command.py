# commands/text_fonts/ascii_command.py
import asyncio
import pyfiglet # For ASCII art generation

async def handle_ascii(message, args, client, bot_instance):
    """
    Handles the /ascii command.
    Converts text into ASCII art using pyfiglet.
    Usage: /ascii <text>
           /ascii <font_name> <text>  (To use a specific font)
           /ascii list_fonts         (To see available Figlet fonts)
    """
    command_name = "ascii"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply(f"Usage: /{command_name} <text> or /{command_name} <font> <text> or /{command_name} list_fonts")
        return

    if args[0].lower() == "list_fonts":
        try:
            available_fonts = pyfiglet.FigletFont.getFonts()
            # Send a few at a time if the list is too long for one message
            max_fonts_per_message = 30
            font_list_str = "Available FIGlet fonts:\n"
            if not available_fonts:
                if hasattr(message, 'reply'): await message.reply("No FIGlet fonts found or pyfiglet not installed correctly.")
                return

            for i in range(0, len(available_fonts), max_fonts_per_message):
                chunk = available_fonts[i:i + max_fonts_per_message]
                if hasattr(message, 'reply'): await message.reply(font_list_str + ", ".join(chunk))
                font_list_str = "" # Only print header for the first message
            if not hasattr(message, 'reply'): print("Available fonts: " + ", ".join(available_fonts))

        except Exception as e:
            print(f"Error listing fonts: {e}")
            if hasattr(message, 'reply'): await message.reply("Error listing fonts.")
        return

    font_name = "standard" # Default font
    text_to_convert = ""

    if len(args) >= 2 and args[0] in pyfiglet.FigletFont.getFonts():
        font_name = args[0]
        text_to_convert = " ".join(args[1:])
    elif len(args) >= 1:
        text_to_convert = " ".join(args)

    if not text_to_convert: # Should have been caught by the first check, but as a safeguard
        if hasattr(message, 'reply'): await message.reply("Please provide text to convert.")
        return

    try:
        fig = pyfiglet.Figlet(font=font_name)
        ascii_art = fig.renderText(text_to_convert)

        # WhatsApp messages often look better with monospace for ASCII art
        # We'll send it in a code block
        reply_text = f"```\n{ascii_art}\n```"

        if hasattr(message, 'reply'):
            await message.reply(reply_text)
        else:
            print(f"ASCII art for '{text_to_convert}' using font '{font_name}':\n{ascii_art}")

    except pyfiglet.FontNotFound:
        if hasattr(message, 'reply'): await message.reply(f"Font '{font_name}' not found. Use `/{command_name} list_fonts` to see available fonts.")
    except Exception as e:
        print(f"Error generating ASCII art: {e}")
        if hasattr(message, 'reply'): await message.reply("An error occurred while generating ASCII art.")


if __name__ == '__main__':
    class MockMessage:
        def __init__(self, text, sender):
            self.text = text
            self.sender = sender
        async def reply(self, text_content):
            # Simulate max message length for font list
            if "Available FIGlet fonts:" in text_content and len(text_content) > 1000: # Arbitrary length
                print(f"BOT REPLIED TO {self.sender} (chunked):\n{text_content[:500]}...")
            else:
                print(f"BOT REPLIED TO {self.sender}:\n{text_content}")


    class MockClient: pass
    class MockBotInstance: pass

    async def main_test():
        mock_bot = MockBotInstance()
        mock_client = MockClient()

        print("\n--- ASCII Art Test Cases ---")

        print("\nTest 1: Default font")
        msg_default = MockMessage("/ascii Hello", "TestUserAscii_Default")
        await handle_ascii(msg_default, ["Hello"], mock_client, mock_bot)

        # Pyfiglet has many fonts, 'slant' is a common one.
        print("\nTest 2: Specific font (slant)")
        msg_slant = MockMessage("/ascii slant Goodbye", "TestUserAscii_Slant")
        await handle_ascii(msg_slant, ["slant", "Goodbye"], mock_client, mock_bot)

        print("\nTest 3: List fonts")
        msg_list_fonts = MockMessage("/ascii list_fonts", "TestUserAscii_List")
        await handle_ascii(msg_list_fonts, ["list_fonts"], mock_client, mock_bot)

        print("\nTest 4: Font not found")
        msg_font_not_found = MockMessage("/ascii nonExistentFont Test", "TestUserAscii_NotFound")
        await handle_ascii(msg_font_not_found, ["nonExistentFont", "Test"], mock_client, mock_bot)

        print("\nTest 5: No text provided")
        msg_no_text = MockMessage("/ascii", "TestUserAscii_NoText")
        await handle_ascii(msg_no_text, [], mock_client, mock_bot)

        print("\nTest 6: Text with spaces")
        msg_spaces = MockMessage("/ascii standard Text With Spaces", "TestUserAscii_Spaces")
        await handle_ascii(msg_spaces, ["standard", "Text", "With", "Spaces"], mock_client, mock_bot)

        print("\nTest 7: Default font with multi-word text")
        msg_default_multi = MockMessage("/ascii Multi Word", "TestUserAscii_DefaultMulti")
        await handle_ascii(msg_default_multi, ["Multi", "Word"], mock_client, mock_bot)


    asyncio.run(main_test())
