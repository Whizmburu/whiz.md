# commands/ai_tools/chat_command.py
# Manages an ongoing chat session with an AI model.
# Needs 'openai' or similar, and API key.
# Also needs a way to store chat history per user/chat session.
# This can be complex (in-memory with limits, or database).

import openai # Placeholder for actual SDK
from datetime import datetime, timedelta

# In-memory storage for chat sessions (lost on restart)
# Structure: {user_id: {"history": [{"role": "user/assistant", "content": "text"}], "last_active": datetime}}
CHAT_SESSIONS = {}
SESSION_TIMEOUT_MINUTES = 15 # Reset session if inactive for this long

async def handle_chat(message, args, client, bot_instance):
    """
    Handles the /chat command for ongoing AI chat sessions.
    Example: /chat Hello, how are you?
             /chat end (to end the session)
    """
    user_id = message.sender # Or message.chat_id for group context if bot chats in group
    current_time = datetime.now()

    # Initialize session if not exists or timed out
    if user_id not in CHAT_SESSIONS or \
       (current_time - CHAT_SESSIONS[user_id]["last_active"]) > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        CHAT_SESSIONS[user_id] = {
            "history": [{"role": "system", "content": "You are Whiz-MD, a helpful WhatsApp AI assistant. Keep your responses concise and friendly."}],
            "last_active": current_time
        }
        if args and args[0].lower() != "end": # Don't send welcome if user immediately says 'end'
             await message.reply("👋 New AI chat session started! Type `/chat end` to finish.")
    else:
        CHAT_SESSIONS[user_id]["last_active"] = current_time

    if not args:
        await message.reply("Continue your chat, or type `/chat end` to finish the session.\n"
                           f"Current session history length: {len(CHAT_SESSIONS[user_id]['history'])-1} exchanges.")
        return

    user_input = " ".join(args)

    if user_input.lower() == "end":
        if user_id in CHAT_SESSIONS:
            del CHAT_SESSIONS[user_id]
            await message.reply("💬 AI chat session ended. Hope to talk to you soon!")
        else:
            await message.reply("No active AI chat session to end.")
        return

    api_key = bot_instance.config.openai_api_key
    if not api_key:
        await message.reply("⚠️ AI chat service API key is not configured. This command is unavailable.")
        if user_id in CHAT_SESSIONS: del CHAT_SESSIONS[user_id] # Clean up session
        return

    # Add user message to history
    CHAT_SESSIONS[user_id]["history"].append({"role": "user", "content": user_input})

    # Prune history if it gets too long (e.g., keep last N messages)
    max_history_len = 10 # System msg + 9 user/assistant pairs (approx)
    if len(CHAT_SESSIONS[user_id]["history"]) > max_history_len:
        # Keep system message and trim older messages
        CHAT_SESSIONS[user_id]["history"] = [CHAT_SESSIONS[user_id]["history"][0]] + CHAT_SESSIONS[user_id]["history"][-max_history_len+1:]


    # openai.api_key = api_key # Example for older openai lib
    try:
        # Example using hypothetical OpenAI client
        # from openai import OpenAI
        # ai_client = OpenAI(api_key=api_key)
        # response = ai_client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=CHAT_SESSIONS[user_id]["history"]
        # )
        # ai_response_text = response.choices[0].message.content.strip()

        # Placeholder response:
        await asyncio.sleep(0.8) # Simulate API call
        ai_response_text = f"AI thinking... You said: \"{user_input[:50]}...\".\n" \
                           f"This is a placeholder AI response. (Session length: {len(CHAT_SESSIONS[user_id]['history'])})"

        # Add AI response to history
        CHAT_SESSIONS[user_id]["history"].append({"role": "assistant", "content": ai_response_text})
        response_message = ai_response_text # Direct reply, no "AI Response:" prefix for chat feel

    except openai.APIError as e:
        # bot_instance.logger.error(f"OpenAI API error for /chat: {e}", exc_info=True)
        print(f"OpenAI API error for /chat: {e}")
        response_message = f"⚠️ Sorry, there was an error communicating with the AI: {str(e)}\nSession might be affected."
        # Optionally remove last user message from history if API call failed
        if CHAT_SESSIONS[user_id]["history"] and CHAT_SESSIONS[user_id]["history"][-1]["role"] == "user":
            CHAT_SESSIONS[user_id]["history"].pop()
    except Exception as e:
        # bot_instance.logger.error(f"Unexpected error in /chat: {e}", exc_info=True)
        print(f"Unexpected error in /chat: {e}")
        response_message = f"⚠️ An unexpected error occurred: {str(e)}"
        if CHAT_SESSIONS[user_id]["history"] and CHAT_SESSIONS[user_id]["history"][-1]["role"] == "user":
            CHAT_SESSIONS[user_id]["history"].pop()


    # await message.reply(response_message) # Placeholder
    print(f"Output for /chat (to {user_id}):\n{response_message}")
    print("Reminder: An AI library, API key, and session management are crucial for /chat.")

if __name__ == '__main__':
    import asyncio
    import os

    class MockMessage:
        def __init__(self, sender="ChatUser1"):
            self.sender = sender
        async def reply(self, text):
            print(f"BOT REPLIED to {self.sender}: {text}")

    class MockConfig:
        def __init__(self):
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                print("TEST INFO: OPENAI_API_KEY not found. /chat will simulate.")
                self.openai_api_key = "sk-dummykeyforchat"

    class MockBotInstance:
        def __init__(self):
            self.config = MockConfig()

    mock_bot = MockBotInstance()

    async def test_chat():
        user1_msg = MockMessage("User1")
        user2_msg = MockMessage("User2") # Different user for separate session

        print("--- Test User1: Start chat & ask question ---")
        await handle_chat(user1_msg, ["Hello", "AI," ,"tell", "me", "about", "Python."], None, mock_bot)

        print("\n--- Test User1: Follow-up question ---")
        await handle_chat(user1_msg, ["What", "are", "its", "main", "uses?"], None, mock_bot)

        print("\n--- Test User2: Start different chat ---")
        await handle_chat(user2_msg, ["Hi", "there!", "What's", "the", "weather", "like?"], None, mock_bot)

        print("\n--- Test User1: End chat ---")
        await handle_chat(user1_msg, ["end"], None, mock_bot)

        print("\n--- Test User1: Try chatting after ending (should start new session) ---")
        await handle_chat(user1_msg, ["Are", "you", "still", "there?"], None, mock_bot)
        await handle_chat(user1_msg, ["end"], None, mock_bot) # End new session

        print("\n--- Test User2: No arguments (should get prompt to continue) ---")
        await handle_chat(user2_msg, [], None, mock_bot)
        await handle_chat(user2_msg, ["end"], None, mock_bot) # End user2 session

        # Test session timeout (conceptual, requires actual time passing or mocking time)
        # CHAT_SESSIONS["UserTimeOut"] = {"history": [], "last_active": datetime.now() - timedelta(minutes=SESSION_TIMEOUT_MINUTES + 5)}
        # print("\n--- Test UserTimeOut: Chat after timeout (should start new) ---")
        # await handle_chat(MockMessage("UserTimeOut"), ["I'm back!"], None, mock_bot)
        # await handle_chat(MockMessage("UserTimeOut"), ["end"], None, mock_bot)


        original_key = mock_bot.config.openai_api_key
        mock_bot.config.openai_api_key = None
        print("\n--- Test No API Key: Start chat ---")
        await handle_chat(MockMessage("NoKeyUser"), ["This", "won't", "work"], None, mock_bot)
        mock_bot.config.openai_api_key = original_key

        print(f"\nFinal CHAT_SESSIONS state: {CHAT_SESSIONS}")


    asyncio.run(test_chat())
