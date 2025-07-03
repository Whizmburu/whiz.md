# commands/utility/calc_command.py
import math
from asteval import Interpreter # For safe evaluation of math expressions
import asyncio

# Create an asteval interpreter instance
# This can be global or created per call. Global might be slightly more efficient.
aeval = Interpreter()
# Disable certain potentially harmful names/functions from asteval's symbol table if needed,
# though by default it's much safer than eval().
# For example, to remove 'while_loop' or 'if_statement' if they were enabled:
# del aeval.symtable['while_loop']
# By default, asteval does not allow imports or file access.

async def handle_calc(message, args, client, bot_instance):
    """
    Handles the /calc command.
    Performs mathematical calculations using asteval for safety.
    Example: /calc 2 + 2 * (3**2) / 4 - 1  (Note: use ** for power)
    """
    if not args:
        # Use reply from message object if available (for actual bot) else print (for test)
        reply_target = getattr(message, 'reply', print)
        await reply_target("Usage: `/calc <mathematical_expression>`\nExample: `/calc 2+2*3**2` (use ** for power)")
        return

    expression = "".join(args)
    # asteval handles common math syntax including parentheses and operator precedence.
    # It also supports common math functions if they are in its symbol table (many are by default).

    # Users might use '^' for power, asteval uses Python's '**'
    # It's good practice to inform users or replace it.
    # For now, let's assume users will use Pythonic syntax or we mention it in help.
    # Or, we can replace ^ with ** before evaluation:
    expression_for_eval = expression.replace('^', '**')

    try:
        # Evaluate the expression using asteval
        # The result = aeval.eval(expression_for_eval) might also work directly
        # Or use aeval.parse and then aeval.run
        aeval(expression_for_eval) # This evaluates and stores result in aeval.symtable['result'] if it's an expression
                                   # Or directly returns the result if it's a simple value.
                                   # More robustly:

        # Clear previous errors
        aeval.error = []
        # Evaluate the expression
        result = aeval.eval(expression_for_eval)

        if aeval.error: # Check for errors collected by asteval
            # Join all error messages
            error_messages = "\n".join([err.get_error()[1] for err in aeval.error])
            response_message = f"⚠️ Error calculating: `{expression}`\n   `{error_messages}`\n   Please check your expression (use ** for power)."
        elif result is None and expression_for_eval.strip(): # Check if expression was non-empty but result is None (e.g. assignment)
            response_message = f"⚠️ Invalid expression or no result: `{expression}`. Please provide a valid mathematical expression."
        else:
            response_message = f"🧮 Result: `{expression}` = `{result}`"

    except Exception as e: # Catch any other unexpected errors from asteval or logic
        response_message = f"⚠️ An unexpected error occurred: `{str(e)}`"
        # Log the full error for debugging: bot_instance.logger.error(f"Calc error: {e}", exc_info=True)

    reply_target = getattr(message, 'reply', print)
    await reply_target(response_message)


if __name__ == '__main__':
    import asyncio
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
