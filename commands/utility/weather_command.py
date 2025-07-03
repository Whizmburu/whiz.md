# commands/utility/weather_command.py
# Needs a weather API provider and a library to make HTTP requests, e.g., 'requests' or 'aiohttp'.
# Also, an API key for the weather service, stored in .env.
# Example: OpenWeatherMap API.
# Add 'requests' or 'aiohttp' to requirements.txt.
import json
import requests # Using 'requests' for simplicity in this example. 'aiohttp' for async.

async def handle_weather(message, args, client, bot_instance):
    """
    Handles the /weather command.
    Fetches weather information for a specified city.
    Example: /weather London
             /weather Paris,FR
    """
    if not args:
        await message.reply("Usage: `/weather <city_name>` or `/weather <city_name>,<country_code>`\n"
                          "Example: `/weather New York` or `/weather London,UK`")
        return

    city = " ".join(args)
    api_key = bot_instance.config.openweathermap_api_key # Needs to be in .env and Config class

    if not api_key:
        await message.reply("⚠️ Weather service API key is not configured. Please contact the bot owner.")
        print("Error: OpenWeatherMap API key not found in config.")
        return

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + city + "&units=metric" # units=metric for Celsius

    try:
        # In an async function, use an async HTTP client like aiohttp
        # For this placeholder with 'requests':
        # loop = asyncio.get_event_loop()
        # response = await loop.run_in_executor(None, requests.get, complete_url)
        # For now, direct call with note:
        print("Note: Using synchronous 'requests' in async function. Consider 'aiohttp'.")
        response = requests.get(complete_url)
        data = response.json()

        if data["cod"] != 200: # Error code from OpenWeatherMap
            error_message = data.get("message", "Unknown error.")
            await message.reply(f"⚠️ Could not fetch weather for `{city}`. Error: {error_message}")
            return

        main = data["main"]
        weather_desc = data["weather"][0]["description"]
        temp = main["temp"]
        feels_like = main["feels_like"]
        humidity = main["humidity"]
        wind_speed = data["wind"]["speed"] # m/s
        country = data["sys"]["country"]
        city_name = data["name"]

        response_message = (
            f"🌤️ **Weather in {city_name}, {country}** 🌦️\n"
            f"-------------------------------------------\n"
            f"🌡️ **Temperature:** {temp}°C (Feels like: {feels_like}°C)\n"
            f"🌬️ **Condition:** {weather_desc.capitalize()}\n"
            f"💧 **Humidity:** {humidity}%\n"
            f"💨 **Wind Speed:** {wind_speed} m/s\n"
            f"-------------------------------------------"
        )

    except requests.exceptions.RequestException as e:
        # bot_instance.logger.error(f"Weather API request error: {e}", exc_info=True)
        print(f"Weather API request error: {e}")
        response_message = f"⚠️ Sorry, I couldn't connect to the weather service."
    except (KeyError, IndexError, TypeError) as e:
        # bot_instance.logger.error(f"Weather data parsing error: {e}", exc_info=True)
        print(f"Weather data parsing error: {e} - Data: {data if 'data' in locals() else 'N/A'}")
        response_message = f"⚠️ Sorry, I couldn't parse the weather data for `{city}`."
    except Exception as e:
        # bot_instance.logger.error(f"Unexpected weather error: {e}", exc_info=True)
        print(f"Unexpected weather error: {e}")
        response_message = f"⚠️ An unexpected error occurred while fetching weather."

    # await message.reply(response_message) # Placeholder
    print(f"Output for /weather:\n{response_message}")
    print("Reminder: 'requests' (or 'aiohttp') library and an OpenWeatherMap API key are required.")


if __name__ == '__main__':
    import asyncio
    # This test will fail without a real API key and network access.
    # It's structured to show how it would be called.

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    class MockConfig:
        def __init__(self):
            # Replace with a real key to test, or expect failure.
            self.openweathermap_api_key = os.getenv("OPENWEATHERMAP_API_KEY") # Try to get from env for local test
            if not self.openweathermap_api_key:
                 print("TEST INFO: OPENWEATHERMAP_API_KEY not found in env. Weather command test will likely fail to fetch real data.")
                 self.openweathermap_api_key = "YOUR_API_KEY_HERE" # Placeholder if not in env

    class MockBotInstance:
        def __init__(self):
            self.config = MockConfig()
            # self.logger = logging.getLogger(__name__) # Example logger

    mock_msg = MockMessage()
    mock_bot = MockBotInstance()

    async def test_weather():
        if mock_bot.config.openweathermap_api_key == "YOUR_API_KEY_HERE":
            print("Skipping weather test as API key is a placeholder.")
            await mock_msg.reply("⚠️ Weather service API key is not configured. Please contact the bot owner.")
            return

        print("--- Test 1: Weather for London ---")
        await handle_weather(mock_msg, ["London"], None, mock_bot)

        print("\n--- Test 2: Weather for a non-existent city ---")
        await handle_weather(mock_msg, ["NonExistentCity123"], None, mock_bot)

        print("\n--- Test 3: No arguments ---")
        await handle_weather(mock_msg, [], None, mock_bot)

    asyncio.run(test_weather())
