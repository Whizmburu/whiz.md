# commands/utility/reminder_command.py
# This is a complex command requiring persistent storage and a scheduling mechanism.
# For a simple bot, reminders might be in-memory and lost on restart.
# For robust reminders: database (SQLite, Redis, etc.) + scheduler (APScheduler, asyncio tasks).
# Add 'APScheduler' or other chosen scheduler to requirements.txt if implementing persistent reminders.
# Add 'parsedatetime' for flexible time string parsing.

import asyncio
import parsedatetime as pdt # For parsing human-readable time strings
from datetime import datetime, timedelta

# In-memory storage for reminders (lost on restart)
# Structure: {chat_id_or_user_id: [{ "time": datetime_obj, "message": "text", "job_id": "some_id"}]}
# A real implementation would use a database.
REMINDERS = {}
# A global scheduler instance (e.g., from APScheduler) would be needed for persistent reminders.
# scheduler = None

async def _send_reminder(chat_id, reminder_message, client):
    """Helper function to send the reminder message."""
    # This would use the actual client.send_message(chat_id, text)
    print(f"SENDING REMINDER to {chat_id}: {reminder_message}")
    # await client.send_message(chat_id, f"⏰ **Reminder!** ⏰\n\n{reminder_message}")
    # For testing, we can just print
    if hasattr(client, 'mock_send'): # If client is our mock client for testing
        await client.mock_send(chat_id, f"⏰ **Reminder!** ⏰\n\n{reminder_message}")


async def handle_reminder(message, args, client, bot_instance):
    """
    Handles the /reminder command.
    Sets a reminder for the user.
    Example: /reminder in 10 minutes to check the oven
             /reminder on 2024-12-25 08:00 AM to say Merry Christmas
             /reminder tomorrow at 3pm call John
    """
    if not args:
        await message.reply("Usage: `/reminder <when> to <what_to_remind>`\n"
                          "Examples:\n"
                          "- `/reminder in 30 minutes to take a break`\n"
                          "- `/reminder tomorrow at 10am to attend meeting`\n"
                          "- `/reminder next Friday to submit report`\n"
                          "You can also list your reminders with `/reminder list` (not yet implemented).")
        return

    full_query = " ".join(args)

    # Simplistic split, assumes " to " or " that " separates time from message
    # A more robust parser (NLP or regex) would be better.
    time_str = ""
    reminder_text = ""

    split_keywords = [" to ", " that "]
    split_keyword_used = None

    for keyword in split_keywords:
        if keyword in full_query.lower():
            parts = full_query.split(keyword, 1)
            time_str = parts[0].strip()
            reminder_text = parts[1].strip()
            split_keyword_used = keyword.strip()
            break

    if not reminder_text: # If "to" or "that" not found, assume the whole string is the reminder message and time is "in a bit"
        # This is a fallback, not ideal. User should be specific.
        # For now, let's require the keyword.
        await message.reply("Please specify the reminder time and message using 'to' or 'that'.\n"
                          "Example: `/reminder in 1 hour to check emails`")
        return

    cal = pdt.Calendar()
    now = datetime.now()
    time_struct, parse_status = cal.parseDT(time_str, sourceTime=now)

    if parse_status == 0: # Could not parse the time string
        await message.reply(f"Sorry, I couldn't understand the time: \"{time_str}\".\n"
                          "Try using formats like 'in 5 minutes', 'tomorrow at 3pm', 'next Monday'.")
        return

    reminder_time = time_struct
    if reminder_time <= now:
        # If parsed time is in the past, try to adjust (e.g., "at 5pm" might mean today or tomorrow)
        if reminder_time.time() <= now.time() and reminder_time.date() == now.date(): # Parsed for today but time already passed
             time_struct_tomorrow, _ = cal.parseDT(f"tomorrow {time_str.split('at')[-1].strip() if 'at' in time_str else time_str}", sourceTime=now)
             if time_struct_tomorrow > now:
                 reminder_time = time_struct_tomorrow
                 await message.reply(f"Note: Interpreted \"{time_str}\" as tomorrow since the time has passed for today.")

    if reminder_time <= now:
        await message.reply(f"The reminder time \"{reminder_time.strftime('%Y-%m-%d %H:%M')}\" is in the past. Please specify a future time.")
        return

    delay_seconds = (reminder_time - now).total_seconds()

    # For this placeholder, we'll use asyncio.sleep for an in-memory reminder.
    # This will NOT survive bot restarts.
    # A real implementation would use APScheduler or similar and store in DB.

    user_id = message.sender # Or message.chat_id depending on how you identify users/chats for DMs

    # Store reminder (in-memory example)
    if user_id not in REMINDERS:
        REMINDERS[user_id] = []

    reminder_entry = {
        "time": reminder_time,
        "message": reminder_text,
        "original_query": full_query,
        "job_id": f"reminder_{user_id}_{int(now.timestamp())}" # Unique ID
    }
    REMINDERS[user_id].append(reminder_entry)

    async def schedule_reminder_task():
        await asyncio.sleep(delay_seconds)
        # Check if reminder still exists (e.g., not cancelled - not implemented here)
        found = False
        if user_id in REMINDERS:
            for r in REMINDERS[user_id]:
                if r["job_id"] == reminder_entry["job_id"]:
                    found = True
                    break
            if found:
                await _send_reminder(user_id, reminder_text, client)
                # Remove from in-memory store after sending
                REMINDERS[user_id] = [r for r in REMINDERS[user_id] if r["job_id"] != reminder_entry["job_id"]]
                if not REMINDERS[user_id]:
                    del REMINDERS[user_id]
            else:
                print(f"Reminder {reminder_entry['job_id']} was cancelled or already sent.")
        else:
             print(f"User {user_id} has no reminders, {reminder_entry['job_id']} might have been cleared.")


    asyncio.create_task(schedule_reminder_task()) # Fire and forget

    response_message = (
        f"✅ Reminder set!\n"
        f"**When:** {reminder_time.strftime('%Y-%m-%d %H:%M:%S %Z')} (in approx. {timedelta(seconds=int(delay_seconds))})\n"
        f"**What:** {reminder_text}"
    )
    # await message.reply(response_message) # Placeholder
    print(f"Output for /reminder:\n{response_message}")
    print("Reminder: 'parsedatetime' library is required. For persistent reminders, a scheduler and DB are needed.")
    print(f"Current in-memory reminders for {user_id}: {REMINDERS.get(user_id)}")


if __name__ == '__main__':
    class MockMessage:
        def __init__(self, sender="TestUser123"):
            self.sender = sender
        async def reply(self, text):
            print(f"BOT REPLIED to {self.sender}: {text}")

    class MockClient: # To simulate message sending for the reminder itself
        async def mock_send(self, user_id, text):
            print(f"\n--- MOCK CLIENT SEND ---")
            print(f"To: {user_id}\nText: {text}")
            print(f"------------------------\n")


    mock_msg = MockMessage()
    mock_client = MockClient()

    async def test_reminder():
        print("--- Test 1: Reminder in seconds ---")
        # Note: Test output for actual reminder might appear later due to asyncio.sleep
        await handle_reminder(mock_msg, ["in", "3", "seconds", "to", "test", "short", "delay"], mock_client, None)

        print("\n--- Test 2: Reminder for 'tomorrow at 10am' ---")
        await handle_reminder(mock_msg, ["tomorrow", "at", "10am", "to", "check", "calendar"], mock_client, None)

        print("\n--- Test 3: Invalid time string ---")
        await handle_reminder(mock_msg, ["gibberish", "time", "to", "do", "nothing"], mock_client, None)

        print("\n--- Test 4: No arguments ---")
        await handle_reminder(mock_msg, [], mock_client, None)

        print("\n--- Test 5: Time in past ---")
        await handle_reminder(mock_msg, ["yesterday", "to", "regret"], mock_client, None)

        print("\n--- Test 6: Reminder 'next Friday at 2 PM' ---")
        await handle_reminder(mock_msg, ["next", "Friday", "at", "2", "PM", "to", "prepare", "weekend"], mock_client, None)

        # Keep the script running for a bit to see if the short reminder fires
        print("\nWaiting for 5 seconds to see if the short reminder fires...")
        await asyncio.sleep(5)
        print("Test sequence finished.")

    asyncio.run(test_reminder())
