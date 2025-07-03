# commands/fun/__init__.py
from .joke_command import handle_joke
from .meme_command import handle_meme
from .eightball_command import handle_8ball
from .truth_command import handle_truth
from .dare_command import handle_dare
from .ship_command import handle_ship
from .rate_command import handle_rate
from .rps_command import handle_rps
from .coinflip_command import handle_coinflip
from .guess_command import handle_guess

__all__ = [
    "handle_joke", "handle_meme", "handle_8ball", "handle_truth", "handle_dare",
    "handle_ship", "handle_rate", "handle_rps", "handle_coinflip", "handle_guess"
]
