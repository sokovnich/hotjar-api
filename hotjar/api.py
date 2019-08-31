import json
import math
import requests

from typing import Optional

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
        Get current user info.

        :return: user info
        """
        response = self.session.get(self.user_info_url)
        return response.json()

    def get_site_feed(self, site_id: int) -> list:
        """
        Get site feed.

        :param site_id: site id
        :return: site feed
        """
        response = self.session.get(
            f"https://insights.hotjar.com/api/v1/sites/{site_id}/feed"
        )
        return response.json()

    def get_site_statistics(self, site_id: int) -> dict:
        """
        Get site statistics.

        :param site_id: site id
        :return: site statistics
        """

        response = self.session.get(
            f"https://insights.hotjar.com/api/v1/sites/{site_id}/statistics"
        )
        return response.json()

    def get_resources(self, user_id: Optional[int] = None) -> dict:
        """
        Get sites and organizations info.
        If user_id is None, get currently logged user resources.

        :return: resources info
        """
        if not user_id:
            user_id = self.user_id

        response = self.session.get(
            f"https://insights.hotjar.com/api/v1/users/{user_id}/resources"
        )
        return response.json()

    def get_feedback_widgets(self, site_id: int) -> list:
        """
        Get all feedback widgets for specified site.

        :param site_id: site id
        :return: feedback widgets info
        """
        response = self.session.get(
            f"https://insights.hotjar.com/api/v1/sites/{site_id}/feedback"
        )
        return response.json()

    def get_feedbacks(
        self,
        site_id: int,
        widget_id: int,
        _filter: str,
        limit: int = 100
    ) -> list:
        """
        Get feedback list.

        :param site_id: site id
        :param widget_id: feedback widget id
        :param _filter: filter
        get feedbacks received between 2019-01-01 and 2019-02-01:
        'created__ge__2019-01-01,created__le__2019-02-01'
        :param limit: feedbacks limit
        :return: feedback info, list
        """
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
        count = self._get_feedbacks_count(
            _filter=_filter, site_id=site_id, widget_id=widget_id
        )

        limit = count if count < limit else limit

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
            result += response.json()["data"]

            offset += amount

        return result

    def get_sentiments(self, site_id: int, widget_id: int, _filter: str) -> dict:
        """
        Get user sentiments info.

        :param site_id: site id
        :param widget_id: feedback widget id
        :param _filter: filter
        :return: sentiments info
        """
        response = self.session.get(
            f"https://insights.hotjar.com/api/v1/sites/{site_id}/feedback/{widget_id}/responses/sentiment",
            params={"filter": _filter},
        )
        return response.json()

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

    def _get_feedbacks_count(self, site_id: int, widget_id: int, _filter: str) -> int:
        """
        Feedbacks count pre-request

        :param site_id: site id
        :param widget_id: feedback widget id
        :param limit: feedbacks limit
        :param _filter: filter
        :return: feedback info, list
        """
        response = self.session.get(
            f"https://insights.hotjar.com/api/v1/sites/{site_id}/feedback/{widget_id}/responses",
            params=dict(
                fields="id", amount=0, offset=0, count="true", filter={_filter}
            ),
        )

        return response.json()["count"]
