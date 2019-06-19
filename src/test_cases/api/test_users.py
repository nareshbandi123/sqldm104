import pytest
from src.common import make_client
from src.helpers.api_client import APIError
from src.test_cases.base_test import APIBaseTest


@pytest.mark.api
class TestUsersAPI(APIBaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.username = cls.data.login.username
        cls.full_name = cls.data.login.full_name

    @pytest.mark.testrail(id=4085)
    def test_c4085_get_users(self):
        users = self.client.get_users()

        found_main_user = False
        for user in users:
            assert '@' in user.email
            assert user.is_active is not None
            assert user.name is not None
            if user.email == self.username:
                found_main_user = True
                assert user.is_active
                assert user.name == self.full_name
        assert found_main_user

    @pytest.mark.testrail(id=4086)
    def test_c4086_get_user(self):
        main_user = self.client.get_user_by_email(self.username)
        user = self.client.get_user(main_user.id)

        # This checks all fields
        assert user == main_user

    @pytest.mark.testrail(id=4087)
    def test_c4087_get_user_by_email(self):
        user = self.client.get_user_by_email(self.username)
        assert user.is_active
        assert user.name == self.full_name
        assert user.email == self.username

    def test_non_existent_user(self):
        new_client = make_client("noone@nowhere.com", "notarealpassword")
        with pytest.raises(APIError) as e_info:
            new_client.get_milestones(self.project.id)

        error = e_info.value
        assert error.status_code == 401
        assert error.error == 'Authentication failed: invalid or missing user/password or session cookie.'
