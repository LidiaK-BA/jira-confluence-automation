import io
import json
import unittest
from email.message import Message
from unittest.mock import MagicMock, Mock, patch
from urllib.error import HTTPError
from urllib.request import Request

from tools.graph_email_source import EmailMessage, GraphEmailSource, GraphSourceError


def graph_response(payload):
    response = MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps(payload).encode(
        "utf-8"
    )
    return response


def message(message_id, subject):
    return {
        "id": message_id,
        "subject": subject,
        "body": {"content": "Details"},
        "from": {"emailAddress": {"address": "requester@example.test"}},
        "receivedDateTime": "2026-10-14T10:00:00Z",
    }


class GraphEmailSourceTests(unittest.TestCase):
    def test_reads_pages_and_returns_only_cr_messages(self):
        first_url = (
            "https://graph.microsoft.com/v1.0/users/"
            "requester%40example.test/messages?$select=id,subject,body,from,"
            "receivedDateTime&$top=100"
        )
        next_url = "https://graph.microsoft.com/v1.0/users/abc/messages?$skip=1"
        opener = Mock(
            side_effect=[
                graph_response(
                    {
                        "value": [message("1", "[CR] First"), message("2", "Unrelated")],
                        "@odata.nextLink": next_url,
                    }
                ),
                graph_response({"value": [message("3", "Second [CR] item")]}),
            ]
        )

        source = GraphEmailSource(
            "secret-token", "requester@example.test", opener=opener
        )
        result = source.list_messages()

        self.assertEqual(
            result,
            [
                EmailMessage(
                    id="1",
                    subject="[CR] First",
                    body="Details",
                    sender="requester@example.test",
                    received_date="2026-10-14T10:00:00Z",
                ),
                EmailMessage(
                    id="3",
                    subject="Second [CR] item",
                    body="Details",
                    sender="requester@example.test",
                    received_date="2026-10-14T10:00:00Z",
                ),
            ],
        )
        first_request = opener.call_args_list[0].args[0]
        self.assertIsInstance(first_request, Request)
        self.assertEqual(
            first_request.get_header("Authorization"), "Bearer secret-token"
        )
        self.assertIn("body-content-type", first_request.get_header("Prefer"))
        self.assertEqual(opener.call_args_list[1].args[0].full_url, next_url)

    def test_can_target_a_specific_mail_folder(self):
        opener = Mock(return_value=graph_response({"value": []}))
        source = GraphEmailSource(
            "token",
            "user@example.test",
            folder_id="folder/with space",
            opener=opener,
        )

        source.list_messages()

        request = opener.call_args.args[0]
        self.assertIn("/mailFolders/folder%2Fwith%20space/messages?", request.full_url)

    def test_rejects_external_pagination_url(self):
        source = GraphEmailSource(
            "token",
            "user",
            opener=Mock(
                return_value=graph_response(
                    {
                        "value": [],
                        "@odata.nextLink": "https://attacker.example/messages",
                    }
                )
            ),
        )

        with self.assertRaisesRegex(GraphSourceError, "unexpected pagination URL"):
            source.list_messages()

    def test_reports_expired_token_without_leaking_it(self):
        headers = Message()
        error = HTTPError(
            "https://graph.microsoft.com/v1.0/users/user/messages",
            401,
            "Unauthorized",
            headers,
            io.BytesIO(b""),
        )
        source = GraphEmailSource(
            "secret-token", "user", opener=Mock(side_effect=error)
        )

        with self.assertRaisesRegex(GraphSourceError, "token may have expired") as raised:
            source.list_messages()

        self.assertNotIn("secret-token", str(raised.exception))

    def test_retries_throttled_request(self):
        headers = Message()
        headers["Retry-After"] = "0"
        throttled = HTTPError(
            "https://graph.microsoft.com/v1.0/users/user/messages",
            429,
            "Too Many Requests",
            headers,
            io.BytesIO(b""),
        )
        opener = Mock(side_effect=[throttled, graph_response({"value": []})])
        source = GraphEmailSource("token", "user", opener=opener)

        with patch("tools.graph_email_source.time.sleep") as sleep:
            self.assertEqual(source.list_messages(), [])

        self.assertEqual(opener.call_count, 2)
        sleep.assert_called_once_with(0)


if __name__ == "__main__":
    unittest.main()
