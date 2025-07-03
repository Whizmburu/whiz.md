# commands/internet/__init__.py
from .news_command import handle_news
from .wiki_command import handle_wiki
from .movie_command import handle_movie
from .anime_command import handle_anime
from .github_command import handle_github
from .npm_command import handle_npm

__all__ = [
    "handle_news", "handle_wiki", "handle_movie", "handle_anime",
    "handle_github", "handle_npm"
]
