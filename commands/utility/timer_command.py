# commands/utility/timer_command.py
# Similar to reminder, but usually simpler: just counts down and announces.
# Can use asyncio.sleep for in-memory timers.
# 'parsedatetime' can be useful here too.

import asyncio
import parsedatetime as pdt
from datetime import datetime, timedelta

# In-memory storage for active timers (lost on restart)
# Structure: {chat_id_or_user_id: [{"name": "optional_name", "end_time": datetime_obj, "task": asyncio.Task}]}
ACTIVE_TIMERS = {}

async def _announce_timer_end(chat_id, timer_name, client):
    message = f"⏱️ **Timer Finished!** ⏱️"
    if timer_name:
        message += f"\nTimer: `{timer_name}`"

    # await client.send_message(chat_id, message)
    print(f"ANNOUNCING TIMER END to {chat_id}: {message}")
    if hasattr(client, 'mock_send'):
        await client.mock_send(chat_id, message)


async def handle_timer(message, args, client, bot_instance):
    """
    Handles the /timer command.
    Sets a countdown timer.
    Example: /timer 5 minutes for pizza
             /timer 30s
             /timer 1h 15m quick nap
    """
    if not args:
        await message.reply("Usage: `/timer <duration> [name_for_timer]`\n"
                          "Examples:\n"
                          "- `/timer 10m` (for 10 minutes)\n"
                          "- `/timer 1h30s work session` (1 hour 30 seconds)\n"
                          "- `/timer 45 seconds quick check`\n"
                          "To list/cancel timers: `/timer list`, `/timer cancel <id>` (not yet implemented).")
        return

    # Try to parse duration and name
    # A bit more complex as duration can have spaces (e.g. "1 hour")
    # and name can also have spaces.
    # We'll use parsedatetime to determine the end of the duration string.

    cal = pdt.Calendar()
    now = datetime.now()

    # Find where the time string ends and the name begins
    time_str_parts = []
    name_parts = []
    time_str_parsed = False

    # Iterate through args to find the end of the time expression recognized by parsedatetime
    # This is a heuristic. A more robust parser would be better.
    current_test_str = ""
    last_successful_parse_len = 0

    for i, arg_part in enumerate(args):
        temp_str = (current_test_str + " " + arg_part).strip()
        time_struct, parse_status = cal.parseDT(temp_str, sourceTime=now)

        if parse_status > 0 and time_struct > now : # Successfully parsed a future time
            current_test_str = temp_str
            last_successful_parse_len = i + 1
            time_str_parsed = True
        else: # If parse fails or is not in future, assume this arg is part of the name
            if time_str_parsed: # if we had a successful parse, the rest is name
                 name_parts = args[i:]
                 break
            # else, keep accumulating, maybe it's like "1 hour 30 minutes"
            # but if nothing parsed yet, this part is still potentially time
            # This simple loop won't handle "1 hour pizza 30 minutes" well.
            # For now, assume name comes strictly after duration.

    if not time_str_parsed: # No valid time duration found at the beginning
        await message.reply(f"Sorry, I couldn't understand the duration from: `{' '.join(args)}`.\n"
                            "Try formats like '5m', '1h 30s', '2 minutes'.")
        return

    time_str = current_test_str
    timer_name = " ".join(name_parts).strip() if name_parts else None


    # Recalculate the final duration based on the determined time_str
    parsed_target_time, _ = cal.parseDT(time_str, sourceTime=now)
    delay_seconds = (parsed_target_time - now).total_seconds()

    if delay_seconds <= 0:
        await message.reply("Please specify a positive duration for the timer.")
        return

    user_id = message.sender # Or chat_id

    # Simple in-memory timer using asyncio.sleep
    # A real bot might want to list/cancel timers, needing more robust management.

    async def timer_task_function(duration, name_of_timer):
        await asyncio.sleep(duration)
        # Check if it wasn't cancelled (not implemented here)
        await _announce_timer_end(user_id, name_of_timer, client)
        # Clean up from ACTIVE_TIMERS (simplified)
        if user_id in ACTIVE_TIMERS:
            ACTIVE_TIMERS[user_id] = [t for t in ACTIVE_TIMERS[user_id] if t["name"] != name_of_timer or t["end_time"] != parsed_target_time] # very basic removal
            if not ACTIVE_TIMERS[user_id]: del ACTIVE_TIMERS[user_id]


    task = asyncio.create_task(timer_task_function(delay_seconds, timer_name))

    # Store active timer (simplified)
    if user_id not in ACTIVE_TIMERS:
        ACTIVE_TIMERS[user_id] = []
    ACTIVE_TIMERS[user_id].append({
        "name": timer_name,
        "end_time": parsed_target_time,
        "task": task,
        "id": f"timer_{user_id}_{int(now.timestamp())}"
    })

    duration_str = str(timedelta(seconds=int(delay_seconds)))
    response_message = f"⏱️ Timer set for **{duration_str}**."
    if timer_name:
        response_message += f" (Name: `{timer_name}`)"

    # await message.reply(response_message) # Placeholder
    print(f"Output for /timer:\n{response_message}")
    print("Reminder: 'parsedatetime' library is required.")
    # print(f"Active timers for {user_id}: {ACTIVE_TIMERS.get(user_id)}")


if __name__ == '__main__':
    class MockMessage:
        def __init__(self, sender="TimerUser"):
            self.sender = sender
        async def reply(self, text):
            print(f"BOT REPLIED to {self.sender}: {text}")

    class MockClient:
        async def mock_send(self, user_id, text):
            print(f"\n--- MOCK CLIENT SEND (TIMER END) ---")
            print(f"To: {user_id}\nText: {text}")
            print(f"-----------------------------------\n")

    mock_msg = MockMessage()
    mock_client = MockClient()

    async def test_timer():
        print("--- Test 1: Timer for 3 seconds with name ---")
        await handle_timer(mock_msg, ["3", "seconds", "short", "test"], mock_client, None)

        print("\n--- Test 2: Timer for 1 minute (no name) ---")
        # This will run longer than the test script if not managed.
        # For actual testing, use very short durations.
        await handle_timer(mock_msg, ["5s"], mock_client, None) # Changed to 5s for test

        print("\n--- Test 3: Invalid duration ---")
        await handle_timer(mock_msg, ["some", "random", "text"], mock_client, None)

        print("\n--- Test 4: No arguments ---")
        await handle_timer(mock_msg, [], mock_client, None)

        print("\n--- Test 5: Duration '1m 2s' with name 'coffee break' ---")
        await handle_timer(mock_msg, ["1m", "2s", "coffee", "break"], mock_client, None)


        print("\nWaiting for 7 seconds to see if timers fire...")
        await asyncio.sleep(7) # Wait for short timers to complete
        print("Test sequence finished.")

    asyncio.run(test_timer())
