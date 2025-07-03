# commands/text_fonts/zalgo_command.py
import asyncio
try:
    from zalgo_py import zalgo # Preferred library
except ImportError:
    zalgo = None # Fallback if not installed

# Basic manual Zalgo implementation if `zalgo-py` is not available
# This is very rudimentary compared to a dedicated library.
MANUAL_ZALGO_CHARS = {
    'up': [chr(i) for i in range(0x0300, 0x036F)],  # Combining Diacritical Marks
    'down': [chr(i) for i in range(0x0300, 0x036F)], # Using the same set for simplicity, can be varied
    'mid': [chr(i) for i in range(0x0300, 0x036F)]  # Using the same set
}
import random

def generate_manual_zalgo(text, intensity='normal'):
    if not text: return ""
    zalgo_text = ""

    num_up_max = 3
    num_down_max = 3
    num_mid_max = 2

    if intensity == 'max':
        num_up_max = 10
        num_down_max = 10
        num_mid_max = 5
    elif intensity == 'min':
        num_up_max = 1
        num_down_max = 1
        num_mid_max = 1

    for char in text:
        zalgo_text += char
        # Add 'up' diacritics
        for _ in range(random.randint(0, num_up_max)):
            zalgo_text += random.choice(MANUAL_ZALGO_CHARS['up'])
        # Add 'down' diacritics
        for _ in range(random.randint(0, num_down_max)):
            zalgo_text += random.choice(MANUAL_ZALGO_CHARS['down'])
        # Add 'mid' diacritics
        for _ in range(random.randint(0, num_mid_max)):
            zalgo_text += random.choice(MANUAL_ZALGO_CHARS['mid'])
    return zalgo_text


async def handle_zalgo(message, args, client, bot_instance):
    """
    Handles the /zalgo command.
    Converts text into Zalgo text (glitched text).
    Usage: /zalgo <text_to_convert>
           /zalgo <intensity:min/normal/max> <text_to_convert> (if using zalgo-py library)
    """
    command_name = "zalgo"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply(f"Usage: /{command_name} <text> OR /{command_name} <intensity> <text>")
        return

    intensity_arg = "normal"
    text_to_convert = ""

    if len(args) >= 2 and args[0].lower() in ['min', 'normal', 'max', 'mini']: # 'mini' for zalgo-py
        intensity_arg = args[0].lower()
        if intensity_arg == "mini": # zalgo-py uses 'mini'
            pass
        elif intensity_arg == "min": # Map our 'min' to zalgo-py's 'mini' if needed
            intensity_arg = "mini" if zalgo else "min"

        text_to_convert = " ".join(args[1:])
    elif len(args) >= 1:
        text_to_convert = " ".join(args)

    if not text_to_convert:
        if hasattr(message, 'reply'): await message.reply("Please provide text to convert.")
        return

    zalgo_fied_text = ""
    if zalgo:
        try:
            # The zalgo-py library's `zalgo()` function might take intensity directly
            # It seems the library's main function is just `zalgo.zalgoify(text, intensity_level)`
            # where intensity_level is 'mini', 'normal', 'maxi'
            z_intensity = intensity_arg
            if z_intensity == "normal":
                z_intensity = None # zalgo_py's default
            elif z_intensity == "max":
                z_intensity = "maxi"

            zalgo_fied_text = zalgo.zalgoify(text_to_convert, intensity=z_intensity)
        except Exception as e:
            print(f"Error using zalgo-py library: {e}. Falling back to manual method.")
            zalgo_fied_text = generate_manual_zalgo(text_to_convert, intensity=intensity_arg if intensity_arg != 'mini' else 'min') # manual doesn't have 'mini'
    else:
        print("zalgo-py library not found. Using basic manual Zalgo generator.")
        zalgo_fied_text = generate_manual_zalgo(text_to_convert, intensity=intensity_arg if intensity_arg != 'mini' else 'min')


    if hasattr(message, 'reply'):
        await message.reply(zalgo_fied_text)
    else:
        print(f"Original: {text_to_convert}\nZalgo ({intensity_arg}): {zalgo_fied_text}")


if __name__ == '__main__':
    class MockMessage:
        def __init__(self, text, sender):
            self.text = text
            self.sender = sender
        async def reply(self, text_content):
            print(f"BOT REPLIED TO {self.sender}: {text_content}")

    class MockClient: pass
    class MockBotInstance: pass

    async def main_test():
        mock_bot = MockBotInstance()
        mock_client = MockClient()

        print("\n--- Zalgo Text Test Cases ---")

        test_text = "He comes"

        print(f"\nTest 1: Default intensity (using {'zalgo-py' if zalgo else 'manual'} generator)")
        msg1 = MockMessage(f"/zalgo {test_text}", "TestUserZalgo_1")
        await handle_zalgo(msg1, [test_text], mock_client, mock_bot)

        print(f"\nTest 2: Min intensity (using {'zalgo-py' if zalgo else 'manual'} generator)")
        msg2 = MockMessage(f"/zalgo min {test_text}", "TestUserZalgo_2")
        await handle_zalgo(msg2, ["min", test_text], mock_client, mock_bot)

        print(f"\nTest 3: Max intensity (using {'zalgo-py' if zalgo else 'manual'} generator)")
        msg3 = MockMessage(f"/zalgo max {test_text}", "TestUserZalgo_3")
        await handle_zalgo(msg3, ["max", test_text], mock_client, mock_bot)

        if zalgo: # Test specific 'mini' for zalgo-py
            print(f"\nTest 3.1: Mini intensity (zalgo-py specific)")
            msg3_1 = MockMessage(f"/zalgo mini {test_text}", "TestUserZalgo_3.1")
            await handle_zalgo(msg3_1, ["mini", test_text], mock_client, mock_bot)


        print("\nTest 4: No arguments")
        msg4 = MockMessage("/zalgo", "TestUserZalgo_4")
        await handle_zalgo(msg4, [], mock_client, mock_bot)

        print("\nTest 5: Only intensity, no text")
        msg5 = MockMessage("/zalgo max", "TestUserZalgo_5")
        await handle_zalgo(msg5, ["max"], mock_client, mock_bot)

    asyncio.run(main_test())
