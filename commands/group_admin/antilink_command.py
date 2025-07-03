# commands/group_admin/antilink_command.py
import asyncio

async def handle_antilink(message, args, client, bot_instance):
    """
    Handles the /antilink command (Group Admin only).
    Enables or disables automatic link detection and removal for non-admins.
    Usage: /antilink <on|off>
    """
    command_name = "antilink"
    logger = bot_instance.logger # Use the bot's logger instance
    reply_target = getattr(message, 'reply', print)

    # This command should only work in groups.
    # The actual check for message.is_group will depend on the WhatsApp library.
    # For simulation, we'll assume if group_id is present, it's a group.
    group_id = getattr(message, 'group_id', None)
    if not group_id: # If not a group message or group_id not available
        # If message.sender can be a group_id in some mock scenarios, this check might need adjustment.
        # For now, strict check on a dedicated group_id attribute.
        await reply_target("This command can only be used in groups.")
        logger.debug(f"/{command_name} called outside of a group context by {message.sender}.")
        return

    # Placeholder: Permission Check - User must be a group admin
    # is_user_admin = await client.is_group_admin(group_id, message.sender_id) # Hypothetical
    # For simulation, let's assume a mock attribute on the message or a test mode
    is_user_admin_mock = getattr(message, 'is_sender_admin', False) # Mock attribute
    if not is_user_admin_mock:
        await reply_target("⚠️ This command is for group admins only.")
        logger.warning(f"Unauthorized /antilink attempt in group {group_id} by {message.sender}.")
        return

    if not args or args[0].lower() not in ["on", "off"]:
        current_status = bot_instance.group_settings.get(group_id, {}).get('antilink_enabled', False)
        await reply_target(f"Usage: `/antilink <on|off>`\nAnti-link is currently: {'🟢 ON' if current_status else '🔴 OFF'}")
        return

    action = args[0].lower()

    if group_id not in bot_instance.group_settings:
        bot_instance.group_settings[group_id] = {}

    if action == "on":
        bot_instance.group_settings[group_id]['antilink_enabled'] = True
        await reply_target("✅ Anti-link feature has been **enabled** for this group. Links from non-admins may be automatically removed.")
        logger.info(f"Anti-link enabled for group {group_id} by admin {message.sender}.")
    elif action == "off":
        bot_instance.group_settings[group_id]['antilink_enabled'] = False
        await reply_target("✅ Anti-link feature has been **disabled** for this group.")
        logger.info(f"Anti-link disabled for group {group_id} by admin {message.sender}.")

    # The actual link detection and removal logic will be in the main message handler.
    # This command only toggles the setting for the group.

if __name__ == '__main__':
    # Setup for testing
    class MockLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARN: {msg}")
        def debug(self, msg): print(f"DEBUG: {msg}")

    class MockMessage:
        def __init__(self, sender="UserAdmin1", group_id="Group123", is_sender_admin=True):
            self.sender = sender
            self.group_id = group_id # Crucial for group commands
            self.is_sender_admin = is_sender_admin # Mock admin status
        async def reply(self, text_content):
            print(f"BOT REPLIED TO {self.sender} in {self.group_id}: {text_content}")

    class MockClient: pass # Not directly used by this command logic, but passed

    class MockBotInstance:
        def __init__(self):
            self.group_settings = {} # Simulates the bot's main group settings store
            self.logger = MockLogger() # Use mock logger for tests

    mock_bot = MockBotInstance()
    mock_client = MockClient()

    async def test_antilink():
        admin_msg = MockMessage(sender="AdminUser", group_id="TestGroup1", is_sender_admin=True)
        non_admin_msg = MockMessage(sender="NormalUser", group_id="TestGroup1", is_sender_admin=False)
        no_group_msg = MockMessage(sender="UserSolo", group_id=None) # DM simulation

        print("--- Test 1: Enable anti-link by admin ---")
        await handle_antilink(admin_msg, ["on"], mock_client, mock_bot)
        print(f"Group settings after 'on': {mock_bot.group_settings}")

        print("\n--- Test 2: Check status (no args) by admin ---")
        await handle_antilink(admin_msg, [], mock_client, mock_bot)

        print("\n--- Test 3: Disable anti-link by admin ---")
        await handle_antilink(admin_msg, ["off"], mock_client, mock_bot)
        print(f"Group settings after 'off': {mock_bot.group_settings}")

        print("\n--- Test 4: Attempt by non-admin ---")
        await handle_antilink(non_admin_msg, ["on"], mock_client, mock_bot)

        print("\n--- Test 5: Attempt in non-group context ---")
        await handle_antilink(no_group_msg, ["on"], mock_client, mock_bot)

        print("\n--- Test 6: Invalid argument by admin ---")
        await handle_antilink(admin_msg, ["maybe"], mock_client, mock_bot)

    asyncio.run(test_antilink())
