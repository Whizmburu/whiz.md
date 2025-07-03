# commands/ai_tools/codegen_command.py
# Uses an AI model for code generation, e.g., OpenAI's GPT models.
# Add 'openai' to requirements.txt.
# Requires OPENAI_API_KEY in .env.

import openai # Placeholder for actual SDK

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

    # openai.api_key = api_key # Example for older openai lib
    await message.reply(f"💻 Generating code for: \"{prompt_text[:100]}{'...' if len(prompt_text)>100 else ''}\" (Language hint: {language_specified})...")

    try:
        # Example using hypothetical OpenAI client
        # from openai import OpenAI
        # ai_client = OpenAI(api_key=api_key)
        # full_prompt = f"Generate a code snippet in {language_specified if language_specified not in ['an unspecified language (AI will try to infer or use a common one)'] else 'a suitable language'} for the following task: {prompt_text}. Only provide the code block, no explanations before or after, unless the code itself contains comments."

        # response = ai_client.chat.completions.create(
        #     model="gpt-3.5-turbo", # Or a code-specialized model if available
        #     messages=[
        #         {"role": "system", "content": "You are an expert code generation assistant. You output only the raw code requested, preferably in a single code block. If language is not specified, choose the most appropriate one."},
        #         {"role": "user", "content": full_prompt}
        #     ],
        #     temperature=0.2 # Lower temperature for more deterministic code
        # )
        # generated_code = response.choices[0].message.content.strip()

        # Placeholder response:
        await asyncio.sleep(2) # Simulate API call
        generated_code = (
            f"// Placeholder code for: {prompt_text}\n"
            f"// Language: {language_specified}\n"
            f"function placeholderFunction() {{\n"
            f"  console.log(\"This is AI generated code (placeholder).\");\n"
            f"  // API Key used: ...{api_key[-4:]}\n"
            f"}}"
        )
        if language_specified == "python":
             generated_code = (
                f"# Placeholder code for: {prompt_text}\n"
                f"# Language: {language_specified}\n"
                f"def placeholder_function():\n"
                f"    print(\"This is AI generated Python code (placeholder).\")\n"
                f"    # API Key used: ...{api_key[-4:]}\n"
            )


        # Format as a code block for WhatsApp (triple backticks)
        # The language hint in backticks might not render on all WhatsApp versions/clients
        # but is good practice.
        formatted_code_response = f"```{(language_specified if language_specified not in ['an unspecified language (AI will try to infer or use a common one)'] else '')}\n{generated_code}\n```"
        response_message = f"✨ **Generated Code:** ✨\n{formatted_code_response}"

    except openai.APIError as e:
        # bot_instance.logger.error(f"OpenAI API error for /codegen: {e}", exc_info=True)
        print(f"OpenAI API error for /codegen: {e}")
        response_message = f"⚠️ Sorry, there was an error with the AI code generation service: {str(e)}"
    except Exception as e:
        # bot_instance.logger.error(f"Unexpected error in /codegen: {e}", exc_info=True)
        print(f"Unexpected error in /codegen: {e}")
        response_message = f"⚠️ An unexpected error occurred: {str(e)}"

    # await message.reply(response_message) # Placeholder
    print(f"Output for /codegen:\n{response_message}")
    print("Reminder: An AI library (e.g., 'openai') and API key are required.")


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
