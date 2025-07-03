# commands/utility/__init__.py

from .calc_command import handle_calc
from .qr_command import handle_qr
from .translate_command import handle_translate
from .shorturl_command import handle_shorturl
from .weather_command import handle_weather
from .time_command import handle_time
from .reminder_command import handle_reminder
from .timer_command import handle_timer
from .dictionary_command import handle_dictionary
from .quote_command import handle_quote

__all__ = [
    "handle_calc",
    "handle_qr",
    "handle_translate",
    "handle_shorturl",
    "handle_weather",
    "handle_time",
    "handle_reminder",
    "handle_timer",
    "handle_dictionary",
    "handle_quote",
]
