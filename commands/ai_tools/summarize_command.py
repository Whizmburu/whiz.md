# commands/ai_tools/summarize_command.py
# Uses an AI model for text summarization, e.g., via 'openai' library or others like 'transformers'.
# Add 'openai' or 'transformers' (and its model dependencies) to requirements.txt.
# Requires OPENAI_API_KEY (or equivalent) in .env.

from openai import OpenAI, APIError
import asyncio

# Re-use client getter if it's made common, or define locally
_openai_clients_sum = {}
def get_openai_client_sum(api_key):
    if api_key not in _openai_clients_sum:
        _openai_clients_sum[api_key] = OpenAI(api_key=api_key)
    return _openai_clients_sum[api_key]


async def handle_summarize(message, args, client, bot_instance):
    """
    Handles the /summarize command.
    Summarizes a given text or text from a replied-to message.
    Example: /summarize <long text to summarize here>
             (Replying to a message) /summarize
    """
    text_to_summarize = ""

    # Check if replying to a message for text
    # This part depends heavily on the WhatsApp library's message object structure
    # if message.replied_to and message.replied_to.text:
    #     text_to_summarize = message.replied_to.text
    #     if args: # If args are also provided, append them or clarify usage
    #         text_to_summarize += " " + " ".join(args)
    # el
    if args:
        text_to_summarize = " ".join(args)
    else:
        # Check for replied message (conceptual)
        # For now, assume text must be in args if not handling replied messages yet
        if hasattr(message, 'replied_to_text') and message.replied_to_text: # Hypothetical attribute
             text_to_summarize = message.replied_to_text
        else:
            await message.reply("Usage: `/summarize <text_to_summarize>`\n"
                              "Or, reply to a message containing text and use `/summarize`.")
            return

    if not text_to_summarize.strip():
        await message.reply("No text found to summarize.")
        return

    # Basic check for text length
    if len(text_to_summarize) < 100: # Arbitrary short length
        await message.reply("The text is too short to summarize effectively. Please provide a longer text.")
        return

    api_key = bot_instance.config.openai_api_key

    if not api_key:
        await message.reply("⚠️ AI summarization service API key is not configured. This command is unavailable.")
        print("Error: OPENAI_API_KEY not found in config for /summarize command.")
        return

    ai_client = get_openai_client_sum(api_key)
    reply_target = getattr(message, 'reply', print)
    response_message = ""
    summary = ""

    await reply_target(f"📝 Summarizing your text... This might take a moment for long texts (processing first ~3500 chars).")

    try:
        # Limit input text to avoid excessive token usage.
        # Max context for gpt-3.5-turbo is ~4096 tokens. Prompt + text + response.
        # ~3500 chars is roughly 800-1000 tokens.
        max_input_chars = 3500
        truncated_text = text_to_summarize[:max_input_chars]
        if len(text_to_summarize) > max_input_chars:
            await reply_target(f"(Note: Input text was truncated to {max_input_chars} characters for summarization.)")

        prompt_for_summary = f"Please provide a concise summary of the following text:\n\n\"{truncated_text}\""

        # Synchronous client call - consider executor for async.
        completion = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert text summarization assistant. Generate clear, concise summaries."},
                {"role": "user", "content": prompt_for_summary}
            ],
            max_tokens=200  # Adjust max_tokens for desired summary length
        )

        if completion.choices and completion.choices[0].message:
            summary = completion.choices[0].message.content.strip()
            response_message = f"📜 **Summary:**\n\n{summary}"
        else:
            summary = "The AI returned an empty summary."
            response_message = f"⚠️ {summary}"

    except APIError as e:
        print(f"OpenAI API error for /summarize: {e.status_code} - {e.message}")
        error_detail = str(e.message)[:100]
        if e.status_code == 401:
             response_message = "⚠️ OpenAI API Key is invalid. Contact owner."
        elif e.status_code == 429:
            response_message = "⚠️ AI service rate limit exceeded. Try again later."
        elif e.status_code == 500:
            response_message = "⚠️ AI service internal server error. Try again later."
        else:
            response_message = f"⚠️ An API error with the AI summarization service: {error_detail}"
    except Exception as e:
        print(f"Unexpected error in /summarize: {e}")
        response_message = f"⚠️ An unexpected error occurred: {str(e)[:100]}"

    await reply_target(response_message)


if __name__ == '__main__':
    import asyncio
    import os

    class MockMessage:
        def __init__(self, replied_to_text=None):
            # Simulate a replied-to message's text content
            self.replied_to_text = replied_to_text
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    class MockConfig:
        def __init__(self):
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                print("TEST INFO: OPENAI_API_KEY not found. /summarize will simulate.")
                self.openai_api_key = "sk-dummykeyforsummary"

    class MockBotInstance:
        def __init__(self):
            self.config = MockConfig()

    mock_bot = MockBotInstance()

    long_text_example = (
        "The Industrial Revolution was a period of major industrialization and innovation that took place during the late 1700s and early 1800s. "
        "It began in Great Britain and quickly spread throughout the world. This period saw the mechanization of agriculture and textile manufacturing and a revolution in power, "
        "including steam ships and railroads, that affected social, cultural, and economic conditions. "
        "Key inventions included the spinning jenny, power loom, and the steam engine, which transformed production processes and led to the factory system. "
        "Urbanization increased চিঠি as people moved to cities for work, leading to new social challenges."
    ) * 2 # Make it a bit longer

    async def test_summarize():
        print("--- Test 1: Summarize with text in args ---")
        await handle_summarize(MockMessage(), [long_text_example], None, mock_bot)

        print("\n--- Test 2: No arguments (and no replied message in this mock) ---")
        await handle_summarize(MockMessage(), [], None, mock_bot)

        print("\n--- Test 3: Summarize with replied text (mocked) ---")
        msg_with_reply = MockMessage(replied_to_text="This is a shorter replied message that might be too short for a real summary but we test the path. " * 3)
        await handle_summarize(msg_with_reply, [], None, mock_bot) # No args, uses replied_to_text

        print("\n--- Test 4: Text too short ---")
        await handle_summarize(MockMessage(), ["Short", "text."], None, mock_bot)

        original_key = mock_bot.config.openai_api_key
        mock_bot.config.openai_api_key = None
        print("\n--- Test 5: No API Key configured ---")
        await handle_summarize(MockMessage(), [long_text_example], None, mock_bot)
        mock_bot.config.openai_api_key = original_key

    asyncio.run(test_summarize())
