# commands/ai_tools/codegen_command.py
# Uses an AI model for code generation, e.g., OpenAI's GPT models.
# Add 'openai' to requirements.txt.
# Requires OPENAI_API_KEY in .env.

from openai import OpenAI, APIError
import asyncio

# Re-use client getter or define locally
_openai_clients_code = {}
def get_openai_client_code(api_key):
    if api_key not in _openai_clients_code:
        _openai_clients_code[api_key] = OpenAI(api_key=api_key)
    return _openai_clients_code[api_key]

async def handle_codegen(message, args, client, bot_instance):
    """
    Handles the /codegen command.
    Generates code based on a natural language prompt.
    Example: /codegen python function to reverse a string
             /codegen javascript code to make an api call using fetch
    """
    if not args:
        await message.reply("Usage: `/codegen <programming_language> <description_of_code>`\n"
                          "Example: `/codegen python function to calculate factorial`\n"
                          "Example: `/codegen js create a blue button with rounded corners`")
        return

    # A simple way to get language: assume first word is language if it's common (python, js, etc.)
    # A more robust way would be to analyze the prompt or have a dedicated language parameter.
    language_guess = args[0].lower()
    common_languages = ["python", "javascript", "js", "java", "c++", "c#", "go", "ruby", "php", "swift", "kotlin", "html", "css"]

    prompt_text = ""
    language_specified = None

    if language_guess in common_languages:
        language_specified = language_guess
        prompt_text = " ".join(args[1:])
        if not prompt_text:
            await message.reply(f"Please provide a description of the code you want to generate in {language_specified}.")
            return
    else:
        prompt_text = " ".join(args)
        # Could try to infer language from prompt or default to a general one.
        # For now, we'll proceed without a strong language hint to the AI if not given.
        language_specified = "an unspecified language (AI will try to infer or use a common one)"


    api_key = bot_instance.config.openai_api_key

    if not api_key:
        await message.reply("⚠️ AI code generation service API key is not configured. This command is unavailable.")
        print("Error: OPENAI_API_KEY not found in config for /codegen command.")
        return

    ai_client = get_openai_client_code(api_key)
    reply_target = getattr(message, 'reply', print)
    response_message = ""
    generated_code = ""

    await reply_target(f"💻 Generating code for: \"{prompt_text[:100]}{'...' if len(prompt_text)>100 else ''}\" (Language hint: {language_specified}). Please wait...")

    try:
        system_prompt = (
            "You are an expert code generation assistant. You output only the raw code requested, "
            "inside a single markdown code block. If a language is specified, use it. "
            "If language is not specified, choose the most appropriate common language based on the request. "
            "Do not include any explanations outside the code block itself (comments within the code are fine)."
        )

        user_query_for_ai = ""
        if language_specified and language_specified != "an unspecified language (AI will try to infer or use a common one)":
            user_query_for_ai = f"Generate a code snippet in {language_specified} for the following task: {prompt_text}"
        else:
            user_query_for_ai = f"Generate a code snippet for the following task (choose a suitable language): {prompt_text}"

        # Synchronous client call - consider executor for async.
        completion = ai_client.chat.completions.create(
            model="gpt-3.5-turbo", # Or a more code-specialized model like gpt-4 if available/needed
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query_for_ai}
            ],
            temperature=0.2, # Lower temperature for more deterministic and usually correct code
            max_tokens=1000    # Allow for reasonably sized code snippets
        )

        if completion.choices and completion.choices[0].message:
            generated_code = completion.choices[0].message.content.strip()

            # The AI is asked to provide a markdown code block. We'll present it as is.
            # If it doesn't provide markdown, we wrap it.
            if generated_code.startswith("```") and generated_code.endswith("```"):
                formatted_code_response = generated_code
            else:
                # Attempt to infer language from output if not specified for the ``` block
                lang_hint_for_block = language_specified if language_specified not in ['an unspecified language (AI will try to infer or use a common one)'] else ''
                formatted_code_response = f"```{lang_hint_for_block}\n{generated_code}\n```"

            response_message = f"✨ **Generated Code:** ✨\n{formatted_code_response}"
        else:
            generated_code = "The AI returned an empty response for code generation."
            response_message = f"⚠️ {generated_code}"

    except APIError as e:
        print(f"OpenAI API error for /codegen: {e.status_code} - {e.message}")
        error_detail = str(e.message)[:100]
        if e.status_code == 401:
             response_message = "⚠️ OpenAI API Key is invalid. Contact owner."
        elif e.status_code == 429:
            response_message = "⚠️ AI service rate limit exceeded. Try again later."
        else:
            response_message = f"⚠️ An API error with the AI code generation service: {error_detail}"
    except Exception as e:
        print(f"Unexpected error in /codegen: {e}")
        response_message = f"⚠️ An unexpected error occurred: {str(e)[:100]}"

    await reply_target(response_message)


if __name__ == '__main__':
    import asyncio
    import os

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    class MockConfig:
        def __init__(self):
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                print("TEST INFO: OPENAI_API_KEY not found. /codegen will simulate.")
                self.openai_api_key = "sk-dummykeyforcodegen"

    class MockBotInstance:
        def __init__(self):
            self.config = MockConfig()

    mock_msg = MockMessage()
    mock_bot = MockBotInstance()

    async def test_codegen():
        print("--- Test 1: Python code generation ---")
        await handle_codegen(mock_msg, ["python", "function", "to", "add", "two", "numbers"], None, mock_bot)

        print("\n--- Test 2: JavaScript code generation ---")
        await handle_codegen(mock_msg, ["javascript", "alert", "hello", "world"], None, mock_bot)

        print("\n--- Test 3: No language specified ---")
        await handle_codegen(mock_msg, ["Create", "a", "loop", "that", "prints", "1", "to", "5"], None, mock_bot)

        print("\n--- Test 4: No arguments ---")
        await handle_codegen(mock_msg, [], None, mock_bot)

        original_key = mock_bot.config.openai_api_key
        mock_bot.config.openai_api_key = None
        print("\n--- Test 5: No API Key configured ---")
        await handle_codegen(mock_msg, ["python", "this", "will", "fail"], None, mock_bot)
        mock_bot.config.openai_api_key = original_key


    asyncio.run(test_codegen())
