# commands/utility/calc_command.py
import math # For more advanced math functions if needed
# Consider using a library like 'asteval' for safe evaluation of math expressions

async def handle_calc(message, args, client, bot_instance):
    """
    Handles the /calc command.
    Performs mathematical calculations.
    Example: /calc 2 + 2 * (3^2) / 4 - 1
    """
    if not args:
        await message.reply("Usage: `/calc <mathematical_expression>`\nExample: `/calc 2+2*3`")
        return

    expression = "".join(args)

    # VERY IMPORTANT: Directly using eval() is extremely dangerous with arbitrary user input.
    # For a production bot, use a safe math expression evaluator.
    # Examples: asteval, numexpr, or a custom parser.
    # For this placeholder, we'll show the unsafe way with a warning.

    allowed_chars = "0123456789+-*/().^ " # Allow digits, ops, parentheses, power, space
    # A more robust solution would parse the expression properly.
    sanitized_expression = "".join(filter(lambda char: char in allowed_chars, expression))
    # Replace ^ with ** for Python power
    sanitized_expression = sanitized_expression.replace('^', '**')

    if not sanitized_expression:
        await message.reply("Invalid expression. Please use numbers and standard operators (+, -, *, /, ^, ()).")
        return

    try:
        # WARNING: eval() is unsafe with untrusted input.
        # This is a placeholder and should be replaced with a safe evaluation method.
        result = eval(sanitized_expression, {"__builtins__": {}}, math.__dict__) # Provide math functions
        response_message = f"🧮 Result: `{expression}` = `{result}`"
    except (SyntaxError, NameError, TypeError, ZeroDivisionError) as e:
        response_message = f"⚠️ Error calculating: `{expression}`\n   `{str(e)}`\n   Please check your expression."
    except Exception as e:
        response_message = f"⚠️ An unexpected error occurred: `{str(e)}`"
        # Log the full error for debugging: bot_instance.logger.error(f"Calc error: {e}", exc_info=True)

    # await message.reply(response_message) # Placeholder
    print(f"Output for /calc:\n{response_message}")
    if "eval(" in response_message and "unsafe" not in response_message : # crude check
        print("WARNING: The /calc command currently uses eval() which is unsafe for production. Replace with a safe evaluator.")


if __name__ == '__main__':
    import asyncio

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    mock_msg = MockMessage()

    async def test_calc():
        print("--- Test 1: Simple addition ---")
        await handle_calc(mock_msg, ["2", "+", "2"], None, None)

        print("\n--- Test 2: Mixed operations ---")
        await handle_calc(mock_msg, ["10", "*", "(5-2)^2", "/", "3"], None, None)

        print("\n--- Test 3: Division by zero ---")
        await handle_calc(mock_msg, ["5", "/", "0"], None, None)

        print("\n--- Test 4: Invalid expression ---")
        await handle_calc(mock_msg, ["hello", "+", "world"], None, None)

        print("\n--- Test 5: No arguments ---")
        await handle_calc(mock_msg, [], None, None)

        print("\n--- Test 6: Using math functions (e.g. sqrt) ---")
        await handle_calc(mock_msg, ["sqrt(16)"], None, None)


    asyncio.run(test_calc())
