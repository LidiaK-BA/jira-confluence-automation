"""Read [CR]-tagged messages from a Microsoft Graph mailbox."""

import argparse
import json
import os
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen


GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
MAX_THROTTLE_RETRIES = 3
MAX_RETRY_DELAY_SECONDS = 30


class GraphSourceError(RuntimeError):
    """Raised when Microsoft Graph cannot return mailbox messages."""


@dataclass(frozen=True)
class EmailMessage:
    id: str
    subject: str
    body: str
    sender: str
    received_date: str


class GraphEmailSource:
    def __init__(
        self,
        access_token: str,
        user_id: str,
        *,
        folder_id: str | None = None,
        timeout: float = 30,
        opener: Callable[..., object] = urlopen,
        api_base: str = GRAPH_API_BASE,
    ) -> None:
        if not access_token.strip():
            raise ValueError("access_token must not be empty")
        if not user_id.strip():
            raise ValueError("user_id must not be empty")
        self._access_token = access_token
        self._timeout = timeout
        self._opener = opener
        self._api_base = api_base.rstrip("/")

        user_path = quote(user_id, safe="")
        if folder_id:
            folder_path = quote(folder_id, safe="")
            self._messages_url = (
                f"{self._api_base}/users/{user_path}/mailFolders/"
                f"{folder_path}/messages"
            )
        else:
            self._messages_url = f"{self._api_base}/users/{user_path}/messages"

    def list_messages(self) -> list[EmailMessage]:
        """Return mailbox messages whose subject contains the [CR] marker."""
        messages: list[EmailMessage] = []
        next_url: str | None = self._messages_url
        first_page = True

        while next_url is not None:
            if not self._is_graph_url(next_url):
                raise GraphSourceError("Graph returned an unexpected pagination URL")

            page_url = next_url
            if first_page:
                page_url += (
                    "?$select=id,subject,body,from,receivedDateTime"
                    "&$top=100"
                )
                first_page = False

            payload = self._request_json(page_url)
            page_messages = payload.get("value")
            if not isinstance(page_messages, list):
                raise GraphSourceError("Graph response is missing a messages list")

            for item in page_messages:
                messages.append(self._parse_message(item))

            next_link = payload.get("@odata.nextLink")
            if next_link is not None and not isinstance(next_link, str):
                raise GraphSourceError("Graph response has an invalid pagination link")
            next_url = next_link

        return [message for message in messages if "[CR]" in message.subject]

    def _is_graph_url(self, url: str) -> bool:
        base = urlsplit(self._api_base)
        candidate = urlsplit(url)
        return (
            candidate.scheme == base.scheme
            and candidate.netloc == base.netloc
            and candidate.path.startswith(base.path + "/")
        )

    def _request_json(self, url: str) -> dict[str, object]:
        request = Request(
            url,
            headers={
                "Authorization": f"Bearer {self._access_token}",
                "Accept": "application/json",
                "Prefer": 'outlook.body-content-type="text"',
            },
        )
        retries = 0

        while True:
            try:
                with self._opener(request, timeout=self._timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload, dict):
                    raise GraphSourceError("Graph response must be a JSON object")
                return payload
            except HTTPError as error:
                retry_after = (
                    error.headers.get("Retry-After") if error.headers else None
                )
                error.close()
                if error.code in (429, 503) and retries < MAX_THROTTLE_RETRIES:
                    delay = self._retry_delay(retry_after, retries)
                    retries += 1
                    time.sleep(delay)
                    continue

                if error.code == 401:
                    message = (
                        "Graph authentication failed (401); the access token may "
                        "have expired. Refresh the token and try again."
                    )
                elif error.code == 403:
                    message = (
                        "Graph denied mailbox access (403); verify the account and "
                        "read-only mail permissions."
                    )
                elif error.code in (429, 503):
                    message = (
                        f"Graph is still throttling requests (HTTP {error.code}) "
                        f"after {retries} retries."
                    )
                else:
                    message = f"Graph request failed with HTTP {error.code}."
                raise GraphSourceError(message) from error
            except URLError as error:
                raise GraphSourceError(f"Could not connect to Microsoft Graph: {error}") from error
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise GraphSourceError("Graph returned an invalid JSON response") from error

    @staticmethod
    def _retry_delay(retry_after: str | None, retries: int) -> float:
        if retry_after is not None:
            try:
                delay = float(retry_after)
            except ValueError:
                try:
                    retry_date = parsedate_to_datetime(retry_after)
                    delay = retry_date.timestamp() - time.time()
                except (TypeError, ValueError, OverflowError):
                    delay = 2**retries
        else:
            delay = 2**retries
        return max(0, min(delay, MAX_RETRY_DELAY_SECONDS))

    @staticmethod
    def _parse_message(item: object) -> EmailMessage:
        if not isinstance(item, dict):
            raise GraphSourceError("Graph response contains an invalid message")

        message_id = item.get("id")
        subject = item.get("subject", "")
        received_date = item.get("receivedDateTime", "")
        body_info = item.get("body", {})
        from_info = item.get("from", {})
        if (
            not isinstance(message_id, str)
            or not isinstance(subject, str)
            or not isinstance(received_date, str)
            or not isinstance(body_info, dict)
            or not isinstance(from_info, dict)
        ):
            raise GraphSourceError("Graph response contains malformed message fields")

        body = body_info.get("content", "")
        email_address = from_info.get("emailAddress", {})
        if not isinstance(body, str) or not isinstance(email_address, dict):
            raise GraphSourceError("Graph response contains malformed sender or body")
        sender = email_address.get("address", "")
        if not isinstance(sender, str):
            raise GraphSourceError("Graph response contains an invalid sender address")

        return EmailMessage(
            id=message_id,
            subject=subject,
            body=body,
            sender=sender,
            received_date=received_date,
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Retrieve [CR]-tagged messages from a Microsoft Graph mailbox.",
        epilog=(
            "Set GRAPH_ACCESS_TOKEN to a valid token with Mail.Read permission and "
            "GRAPH_USER_ID to the mailbox user's ID or UPN. Optionally set "
            "GRAPH_MAIL_FOLDER_ID. Then run: python tools/graph_email_source.py"
        ),
    )
    parser.add_argument(
        "--folder-id",
        default=os.environ.get("GRAPH_MAIL_FOLDER_ID"),
        help="mail folder ID (defaults to GRAPH_MAIL_FOLDER_ID or the whole mailbox)",
    )
    args = parser.parse_args()

    access_token = os.environ.get("GRAPH_ACCESS_TOKEN")
    user_id = os.environ.get("GRAPH_USER_ID")
    if not access_token:
        parser.error("set GRAPH_ACCESS_TOKEN to a valid Graph access token")
    if not user_id:
        parser.error("set GRAPH_USER_ID to the mailbox user's ID or UPN")

    try:
        source = GraphEmailSource(
            access_token=access_token,
            user_id=user_id,
            folder_id=args.folder_id,
        )
        messages = source.list_messages()
    except (GraphSourceError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(json.dumps([asdict(message) for message in messages], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
