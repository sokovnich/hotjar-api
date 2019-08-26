import json
import math
import requests

from .exceptions import AuthorizationError


class HotjarAPI:
    def __init__(self, email: str, password: str):
        self.login_url = "https://insights.hotjar.com/api/v2/users"
        self.user_info_url = "https://insights.hotjar.com/api/v2/users/me"
        self.headers = {
            "Content-Type": "application/json",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/75.0.3770.90 Chrome/75.0.3770.90 Safari/537.36",
        }

        self.session = requests.Session()
        self.session.headers = self.headers

        login_info = self.login(email=email, password=password)

        self.user_id = login_info["user_id"]
        self.access_key = login_info["access_key"]

    def get_current_user_info(self) -> dict:
        """
        Get current user info

        :return:
        """
        response = self.session.get(self.user_info_url)
        return response.json()

    def get_site_feed(self, site_id):
        response = self.session.get(
            f"https://insights.hotjar.com/api/v1/sites/{site_id}/feed"
        )
        return response.json()

    def get_site_statistics(self, site_id):
        """
        Get site statistics

        :param site_id:
        :return:
        """

        response = self.session.get(
            f"https://insights.hotjar.com/api/v1/sites/{site_id}/statistics"
        )
        return response.json()

    def get_resources(self, user_id=None) -> dict:
        """
        Get sites and organizations info.
        If user_id is None, get currently logged user info.

        :return: info
        """
        if not user_id:
            user_id = self.user_id

        response = self.session.get(
            f"https://insights.hotjar.com/api/v1/users/{user_id}/resources"
        )
        return response.json()

    def get_feedback_widgets(self, site_id):
        response = self.session.get(
            f"https://insights.hotjar.com/api/v1/sites/{site_id}/feedback"
        )
        return response.json()

    def get_feedback(
        self,
        site_id: int,
        widget_id: int,
        limit: int = 100,
        _filter: str = "created__ge__2019-01-21",
    ) -> dict:
        fields = [
            "browser",
            "content",
            "created_datetime_string",
            "created_epoch_time",
            "country_code",
            "country_name",
            "device",
            "id",
            "image_url",
            "index",
            "os",
            "response_url",
            "short_visitor_uuid",
            "thumbnail_url",
            "window_size",
        ]
        amount = 100
        result = []
        offset = 0

        for i in range(math.ceil(limit / 100)):
            params = dict(
                fields=",".join(fields),
                sort="-id",
                amount=amount,
                offset={offset},
                count=True,
                filter={_filter},
            )
            response = self.session.get(
                f"https://insights.hotjar.com/api/v1/sites/{site_id}/feedback/{widget_id}/responses",
                params=params,
            )
            result += response.json()['data']

            offset += amount

        return result

    def login(self, email: str, password: str) -> dict:
        """
        Success response:
        {
            "access_key": "78e5aca7107e4ebaa77db80a0d8511a0",
            "success": true,
            "user_id": 9296871
        }

        :param email: user email
        :param password: user password
        :return: authorization info, dict
        """
        payload = {
            "action": "login",
            "email": email,
            "password": password,
            "remember": True,
        }

        response = self.session.post(self.login_url, data=json.dumps(payload))

        result = response.json()

        if not response.status_code == 200 or "access_key" not in result:
            raise AuthorizationError(response.text)

        return result
