from dataclasses import dataclass
from typing import Tuple
from atproto import Client

@dataclass
class BlueskyCredentials:
    """Data structure for Bluesky authentication"""
    username: str
    password: str

class BlueskyPoster:
    def __init__(self, credentials: BlueskyCredentials, test_mode: bool = False):
        self.credentials = credentials
        self.test_mode = test_mode
        self._client = None

    def _ensure_client(self):
        """Ensure we have an authenticated client"""
        if not self._client:
            self._client = Client()
            self._client.login(self.credentials.username, self.credentials.password)

    def post_content(self, content: str) -> Tuple[bool, str]:
        """Post content to Bluesky or simulate posting in test mode"""
        if self.test_mode:
            return True, f"Test mode - Would post:\n{content}"

        try:
            self._ensure_client()
            response = self._client.post(text=content)
            return True, "Posted successfully"
        except Exception as e:
            return False, str(e)
