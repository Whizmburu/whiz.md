from datetime import datetime

class MessageTemplates:
    def __init__(self, owner_name="WHIZ", bot_name="WHIZ-MD"):
        self.owner_name = owner_name
        self.bot_name = bot_name
        self.logo_url = "https://i.ibb.co/sp1hFpKj/whizmd.png" # WHIZ-MD logo
        self.support_group_link_default = "https://chat.whatsapp.com/JLmSbTfqf4I2Kh4SNJcWgM"

    def get_connected_message(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""\
║️ ✨ {self.bot_name} CONNECTED ✨ ║️
╔══════════════════════════════════╗
║ 🚀 Status     : Online and Active
║ 📅 Timestamp  : {current_time}
║ 🚫 Errors      : None
╚══════════════════════════════════╝
"""
        # The image is usually sent as a separate message or using platform-specific features
        # For text-based representation, we can mention it:
        # message += f"\n> ![whizmd]({self.logo_url})" # Markdown style, may not render in all consoles
        return message

    def get_ping_message(self, ping_time, uptime, load_avg):
        # Determine speed based on ping_time (example thresholds)
        try:
            ping_ms = float(ping_time.replace('ms', ''))
            if ping_ms < 100:
                speed = "Excellent"
            elif ping_ms < 300:
                speed = "Good"
            elif ping_ms < 600:
                speed = "Fair"
            else:
                speed = "Slow"
        except ValueError:
            speed = "N/A"

        message = f"""\
╔═══════[ 📡 PING STATUS ]═══════╗
║ 🔪 Response    : {ping_time}
║ ⚡ Speed       : {speed}
║ 📊 Uptime      : {uptime}
║ 🩸 Load        : {load_avg}
╚══════════════════════════════════╝
"""
        return message

    def get_main_menu(self, owner, repo_url, prefixes, forks, command_count, uptime, support_group_link=None):
        if support_group_link is None:
            support_group_link = self.support_group_link_default

        # The HTML for embedding logo is for platforms that support it.
        # In text-based scenarios, it's often sent as a separate image message or a link.
        # For this template, we'll focus on the text part.
        # The actual clickable logo would be handled by the bot platform's message sending capabilities.

        menu_text = f"""\
╔════[ 🌺 {self.bot_name} MENU 🌺 ]════╗
║ 👑 Owner     : {owner}
║ 📁 Repo      : {repo_url}
║ 🔤 Prefix    : {prefixes}
║ 🍜 Forks     : {forks}
║ 🔹 Commands  : {command_count}
║ ⏱ Uptime    : {uptime}
║
║ 🔹 Use /help or /menu to explore more
║ 📞 Support Group:
║      📣 <click the {self.bot_name} logo below>
╚══════════════════════════════════╝
"""
        # Appending a note about the logo for clarity, actual image sending is separate
        # menu_text += f"\n(To see the clickable logo, ensure your client supports it or check the support group link directly: {support_group_link})"
        # menu_text += f"\nLogo: {self.logo_url}" # Direct link to image

        # The HTML part for the logo:
        # This would typically be sent as part of an HTML message if the platform supports it.
        # For now, we just define it. The bot would need to be able to send rich messages.
        # html_logo_part = f"""
# <div style="text-align:center; margin-bottom: 15px;">
#   <a href="{support_group_link}" target="_blank">
#     <img src="{self.logo_url}" alt="{self.bot_name} Bot Logo" width="180" style="border-radius: 20px; box-shadow: 0 0 10px #00ffcc;">
#   </a>
# </div>
# """
        # In a real bot, you might send the text and then an image, or a combined rich message.
        return menu_text

if __name__ == '__main__':
    templates = MessageTemplates(owner_name="TestOwner", bot_name="TestBot-MD")

    print("--- CONNECTED MESSAGE ---")
    print(templates.get_connected_message())

    print("\n--- PING MESSAGE ---")
    print(templates.get_ping_message(ping_time="75ms", uptime="2h 15m 30s", load_avg="0.5"))

    print("\n--- MAIN MENU ---")
    print(templates.get_main_menu(
        owner="TestOwner",
        repo_url="github.com/Test/Bot",
        prefixes="/ . !",
        forks=100,
        command_count=50,
        uptime="2h 30m",
        support_group_link="https://example.com/support"
    ))
    # The HTML part would be handled differently by the bot depending on platform capabilities.
    # For example, a WhatsApp bot might send an image message with a caption.
    print(f"\nNote: The clickable logo part would be sent as a separate image or rich message with link: {templates.logo_url} linking to {templates.support_group_link_default}")
