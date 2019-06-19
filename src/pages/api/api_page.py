import json

from src.helpers.api_client import APIError
from pathlib import Path, PurePosixPath


class APIPage:
    def assert_object(self, obj):
        assert obj

    def assert_equality(self, obj, obj2):
        assert obj == obj2

    def assert_not_equal(self, obj, obj2):
        assert obj != obj2

    def assert_field_in_object(self, f, obj):
        assert f in obj.__dict__

    def assert_exists(self, objs):
        assert len(objs) > 0

    def assert_length(self, obj, length):
        assert len(obj) == length

    def assert_length_equality(self, obj1, obj2):
        assert len(obj1) == len(obj2)

    def check_response_is_empty(self, resp):
        assert resp is None

    def check_response_is_empty_list(self, resp):
        assert resp == []

    def check_status_code_and_error(self, exc: APIError, expected_code, expected_error, alt_error=None):
        assert exc.status_code == expected_code
        if alt_error:
            assert exc.error_text.startswith(expected_error) or exc.error_text.startswith(alt_error)
        else:
            assert exc.error_text.startswith(expected_error)

    def expect_to_raise_exception(self, callback, args, code, error, alt_error=None):
        try:
            callback(*args)
        except (APIError, Exception) as exc:
            self.check_status_code_and_error(exc, code, error, alt_error)

    def validate_attachments(self, attachments, json_string):
        cmp = json.loads(json_string)
        for c, attach in enumerate(attachments):
            for k, v in cmp[c].items():
                if k == 'size':
                    # Size deviation
                    assert v - 1 <= attach[k] <= v + 1
                else:
                    assert attach[k] == v

    def assert_attachment_content_names_in_attachment_file(self, attachment_content, attachment_file):
        for attachment in attachment_content:
            assert attachment['name'] in attachment_file

    def generate_attachment(self, filename):
        return open(str(Path(PurePosixPath(f'../data/{filename}'))), 'rb')

    def assert_response_code(self, response, code):
        assert response['response_code'] == code

    def assert_response_error(self, response, error):
        assert error in response['response']['error']
