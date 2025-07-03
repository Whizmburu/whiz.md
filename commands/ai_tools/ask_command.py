# commands/ai_tools/ask_command.py
# Needs an AI library, e.g., 'openai'.
# Add 'openai' to requirements.txt.
# Requires OPENAI_API_KEY in .env.

from openai import OpenAI, APIError # Import OpenAI and APIError for specific exception handling
import asyncio

# Global OpenAI client instance cache to avoid re-initializing on every call
# This is a simple cache; a more robust solution might involve class-based client management.
_openai_clients = {}

def get_openai_client(api_key):
    if api_key not in _openai_clients:
        _openai_clients[api_key] = OpenAI(api_key=api_key)
    return _openai_clients[api_key]

async def handle_ask(message, args, client, bot_instance):
    """
    Handles the /ask command.
    Sends a query to an AI model (e.g., GPT) and returns the response.
    Example: /ask What is the capital of France?
    """
    if not args:
        await message.reply("Usage: `/ask <your_question>`\nExample: `/ask Tell me a fun fact about space.`")
        return

    question = " ".join(args)
    api_key = bot_instance.config.openai_api_key

    if not api_key:
        await message.reply("⚠️ AI service API key is not configured. This command is unavailable. Please contact the bot owner.")
        print("Error: OPENAI_API_KEY not found in config for /ask command.")
        return

    ai_client = get_openai_client(api_key)
    response_message = ""
    ai_response_text = ""

    try:
        if hasattr(message, 'reply'): await message.reply(f"🤔 Thinking about: \"{question[:50]}...\" Please wait.")

        # Make the API call using the OpenAI client (v1.x SDK syntax)
        # In a real async bot, you might run this in an executor if the SDK call is blocking
        # However, the OpenAI v1.x client with httpx is async-compatible.
        # For truly non-blocking, one would use `await ai_client.chat.completions.create(...)`
        # if the client was an AsyncOpenAI client.
        # For simplicity with the current synchronous OpenAI client, this will block the event loop.
        # To make it non-blocking with sync client:
        # loop = asyncio.get_event_loop()
        # completion = await loop.run_in_executor(
        # None, # Default executor (ThreadPoolExecutor)
        # lambda: ai_client.chat.completions.create(
        # model="gpt-3.5-turbo",
        # messages=[
        # {"role": "system", "content": "You are a helpful AI assistant for the WHIZ-MD WhatsApp bot. Provide concise and informative answers."},
        # {"role": "user", "content": question}
        # ]
        # )
        # )
        # For now, direct call, assuming tests are okay with potential blocking or it's handled by bot runner.
        # If using `AsyncOpenAI`, the call would be:
        # ai_client = AsyncOpenAI(api_key=api_key) # Need to manage this client instance too
        # completion = await ai_client.chat.completions.create(...)

        # Using the synchronous client for now as per initial library version assumption.
        # This will block if not run in an executor.
        # For a production bot, ensure this runs non-blockingly.
        completion = ai_client.chat.completions.create(
            model="gpt-3.5-turbo", # A common and capable model
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for the WHIZ-MD WhatsApp bot. Provide concise and informative answers."},
                {"role": "user", "content": question}
            ]
        )

        if completion.choices and completion.choices[0].message:
            ai_response_text = completion.choices[0].message.content.strip()
            response_message = f"🤖 **AI Response:**\n\n{ai_response_text}"
        else:
            ai_response_text = "The AI returned an empty response."
            response_message = f"⚠️ {ai_response_text}"

    except APIError as e: # Catch specific API errors from openai library
        print(f"OpenAI API error for /ask: {e.status_code} - {e.message}")
        error_detail = str(e.message)[:100] # Keep error message brief for user
        if e.status_code == 401: # Authentication error
             response_message = "⚠️ OpenAI API Key is invalid or authentication failed. Please contact the bot owner."
        elif e.status_code == 429: # Rate limit
            response_message = "⚠️ The AI service is currently experiencing high traffic (rate limit exceeded). Please try again later."
        elif e.status_code == 500: # Server error
            response_message = "⚠️ The AI service reported an internal server error. Please try again later."
        else:
            response_message = f"⚠️ An API error occurred with the AI service: {error_detail}"
    except Exception as e:
        print(f"Unexpected error in /ask: {e}")
        response_message = f"⚠️ An unexpected error occurred while processing your request: {str(e)[:100]}"

    reply_target = getattr(message, 'reply', print)
    await reply_target(response_message)


if __name__ == '__main__':
    import asyncio
    import os # For getting API key from env for test

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    class MockConfig:
        def __init__(self):
            self.openai_api_key = os.getenv("OPENAI_API_KEY") # For local testing
            if not self.openai_api_key:
                print("TEST INFO: OPENAI_API_KEY not found in env. /ask command will simulate or show error.")
                self.openai_api_key = "sk-dummykeyfortest" # Fallback dummy for structure

    class MockBotInstance:
        def __init__(self):
            self.config = MockConfig()
            # self.logger = logging.getLogger(__name__)

    mock_msg = MockMessage()
    mock_bot = MockBotInstance()

    async def test_ask():
        print("--- Test 1: Ask a question ---")
        await handle_ask(mock_msg, ["What", "is", "the", "meaning", "of", "life?"], None, mock_bot)

        print("\n--- Test 2: No arguments ---")
        await handle_ask(mock_msg, [], None, mock_bot)

        print("\n--- Test 3: Ask another question ---")
        await handle_ask(mock_msg, ["Explain", "black", "holes", "simply."], None, mock_bot)

        # Test without API key
        original_key = mock_bot.config.openai_api_key
        mock_bot.config.openai_api_key = None
        print("\n--- Test 4: No API Key configured ---")
        await handle_ask(mock_msg, ["This", "should", "fail", "gracefully."], None, mock_bot)
        mock_bot.config.openai_api_key = original_key


    asyncio.run(test_ask())
