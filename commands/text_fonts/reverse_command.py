# commands/text_fonts/reverse_command.py
import asyncio

async def handle_reverse(message, args, client, bot_instance):
    """
    Handles the /reverse command.
    Reverses the given text.
    Usage: /reverse <text_to_reverse>
    """
    command_name = "reverse"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply(f"Usage: /{command_name} <text to reverse>")
        return

    text_to_reverse = " ".join(args)
    reversed_text = text_to_reverse[::-1]

    if hasattr(message, 'reply'):
        await message.reply(reversed_text)
    else:
        print(f"Original: {text_to_reverse}\nReversed: {reversed_text}")

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

        print("\n--- Reverse Text Test Cases ---")

        print("\nTest 1: Simple word")
        msg1 = MockMessage("/reverse hello", "TestUserReverse_1")
        await handle_reverse(msg1, ["hello"], mock_client, mock_bot)

        print("\nTest 2: Sentence with spaces")
        msg2 = MockMessage("/reverse hello world", "TestUserReverse_2")
        await handle_reverse(msg2, ["hello", "world"], mock_client, mock_bot)

        print("\nTest 3: Numbers and symbols")
        msg3 = MockMessage("/reverse 123!@#", "TestUserReverse_3")
        await handle_reverse(msg3, ["123!@#"], mock_client, mock_bot)

        print("\nTest 4: Palindrome")
        msg4 = MockMessage("/reverse madam", "TestUserReverse_4")
        await handle_reverse(msg4, ["madam"], mock_client, mock_bot)

        print("\nTest 5: No arguments")
        msg5 = MockMessage("/reverse", "TestUserReverse_5")
        await handle_reverse(msg5, [], mock_client, mock_bot)

        print("\nTest 6: Text with leading/trailing spaces (though args usually strip them)")
        msg6 = MockMessage("/reverse  spaced out  ", "TestUserReverse_6")
        await handle_reverse(msg6, [" spaced", "out "], mock_client, mock_bot)


    asyncio.run(main_test())
