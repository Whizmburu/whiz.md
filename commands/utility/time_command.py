# commands/utility/time_command.py
# Needs 'pytz' library for timezone handling.
# Add 'pytz' to requirements.txt.
import pytz
from datetime import datetime

async def handle_time(message, args, client, bot_instance):
    """
    Handles the /time command.
    Shows the current time in a specified timezone or a list of common timezones.
    Example: /time New_York
             /time Europe/Paris
             /time (shows times for a few major cities)
    """
    if not args:
        # Show time for a few predefined major cities if no args
        major_timezones = {
            "New York (ET)": "America/New_York",
            "London (GMT/BST)": "Europe/London",
            "Paris (CET/CEST)": "Europe/Paris",
            "Tokyo (JST)": "Asia/Tokyo",
            "Sydney (AEST/AEDT)": "Australia/Sydney",
            "UTC": "UTC"
        }
        response_lines = ["🕰️ **Current Times in Major Cities** 🕰️"]
        for city_display, tz_name in major_timezones.items():
            try:
                timezone = pytz.timezone(tz_name)
                time_in_tz = datetime.now(timezone)
                response_lines.append(f"- **{city_display}:** {time_in_tz.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
            except pytz.exceptions.UnknownTimeZoneError:
                response_lines.append(f"- {city_display}: Error fetching time (unknown timezone: {tz_name})")
        response_message = "\n".join(response_lines)
        response_message += "\n\nUsage: `/time <timezone_name>` (e.g., `/time America/Los_Angeles` or `/time London`)"
    else:
        timezone_query = " ".join(args)
        found_tz = None

        # Try direct match first (e.g., "Europe/London")
        if timezone_query in pytz.all_timezones:
            found_tz = timezone_query
        else:
            # Try to find a matching timezone (simple substring search, case-insensitive)
            # This can be improved with fuzzy matching or a more structured search
            normalized_query = timezone_query.lower().replace(" ", "_")
            for tz_name in pytz.all_timezones:
                if normalized_query in tz_name.lower():
                    found_tz = tz_name
                    break

        if found_tz:
            try:
                timezone = pytz.timezone(found_tz)
                time_in_tz = datetime.now(timezone)
                response_message = (
                    f"🕰️ **Current Time** 🕰️\n"
                    f"**Zone:** {found_tz}\n"
                    f"**Time:** {time_in_tz.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
                )
            except pytz.exceptions.UnknownTimeZoneError: # Should not happen if found_tz is from pytz.all_timezones
                response_message = f"⚠️ Error: Could not process timezone `{found_tz}` despite finding it."
        else:
            response_message = (
                f"⚠️ Timezone not found for: `{timezone_query}`.\n"
                f"Please use a valid timezone name (e.g., 'America/New_York', 'Europe/Berlin', 'Asia/Kolkata').\n"
                f"You can find a list here: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
            )

    # await message.reply(response_message) # Placeholder
    print(f"Output for /time:\n{response_message}")
    print("Reminder: 'pytz' library is required.")

if __name__ == '__main__':
    import asyncio

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    mock_msg = MockMessage()

    async def test_time():
        print("--- Test 1: Specific timezone (Europe/Madrid) ---")
        await handle_time(mock_msg, ["Europe/Madrid"], None, None)

        print("\n--- Test 2: Partial timezone name (New York) ---")
        await handle_time(mock_msg, ["New", "York"], None, None) # Should find America/New_York

        print("\n--- Test 3: Invalid timezone ---")
        await handle_time(mock_msg, ["Invalid/Timezone"], None, None)

        print("\n--- Test 4: No arguments (show major cities) ---")
        await handle_time(mock_msg, [], None, None)

        print("\n--- Test 5: Search for 'London' ---")
        await handle_time(mock_msg, ["London"], None, None)

    asyncio.run(test_time())
