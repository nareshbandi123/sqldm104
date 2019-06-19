import pytest
from src.test_cases.base_test import BaseTest
from src.common import decode_data, read_config
from src.models.administration.user import RolePermissions
from src.pages.administration.users_roles_page import UsersRolesPage
from src.pages.administration.site_settings_page import SiteSettingsPage
import time
import copy


class TestUsersRoles(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # Get test data
        cls.users = read_config('../config/users.json')
        cls.sso_settings = read_config('../config/sso_settings.json')

        cls.setup_database(cls.users)

        platform = cls.data.database.dbtype
        if platform == "mssql":
            cls.valid_settings = cls.sso_settings.valid_settings_windows
        elif platform == "mysql":
            cls.valid_settings = cls.sso_settings.valid_settings_linux
        else:
            cls.valid_settings = cls.sso_settings.valid_settings_hosted

        # Prepare page objects
        cls.users_overview_url = cls.data.server_name + cls.users.overview_url
        cls.site_settings_url = cls.data.server_name + cls.sso_settings.site_settings_url
        cls.users_roles = UsersRolesPage(cls.driver)
        cls.site_settings = SiteSettingsPage(cls.driver)

    @classmethod
    def teardown_class(cls):
        cls.teardown_database()
        super().teardown_class()

    def setup_method(self):
        self.users_roles.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)

    def teardown_method(self):
        self.users_roles.open_page(self.data.server_name)
        self.driver.delete_all_cookies()

    @pytest.mark.run(order=1)
    def test_add_user_validation_nothing_inserted(self):
        user = decode_data(str(self.users.add[0]))
        # Nothing inserted
        self.users_roles.open_page(self.data.server_name + self.users.add_user_url)
        self.users_roles.click_add()
        self.users_roles.validate_error_message(self.users.messages.msg_err_user_validation)
        # Email missing
        self.users_roles.clear_name_and_email()
        self.users_roles.add_name_and_email(user.full_name, "")
        self.users_roles.click_add()
        self.users_roles.validate_error_message(self.users.messages.msg_err_user_email_missing)
        # Full Name missing
        self.users_roles.clear_name_and_email()
        self.users_roles.add_name_and_email("", user.email_address)
        self.users_roles.click_add()
        self.users_roles.validate_error_message(self.users.messages.msg_err_user_full_name_missing)
        # Should successfully create the user
        self.users_roles.clear_name_and_email()
        self.users_roles.add_name_and_email(user.full_name, user.email_address)
        self.users_roles.click_add()
        self.users_roles.validate_success_message(self.users.messages.msg_success_added_user_invitation)

    @pytest.mark.testrail(id=97)
    @pytest.mark.dependency(name="test_add_user_with_custom_password")
    @pytest.mark.run(order=2)
    def test_add_user_with_custom_password(self):
        user = decode_data(str(self.users.add[1]))

        self.users_roles.open_page(self.data.server_name + self.users.add_user_url)
        self.users_roles.add_name_and_email(user.full_name, user.email_address)
        self.users_roles.insert_manual_password(user.password)
        self.users_roles.click_add()

        user.id = self.users_roles.retrieve_id_from_link(user.full_name)
        self.users_roles.validate_success_message(self.users.messages.msg_success_added_user_manual_psw)
        self.users_roles.validate_user_data(user)


    @pytest.mark.dependency(name="test_add_user_with_email_invitation")
    @pytest.mark.run(order=3)
    def test_add_user_with_email_invitation(self):
        user = decode_data(str(self.users.add[2]))

        self.users_roles.open_page(self.data.server_name + self.users.add_user_url)
        self.users_roles.add_name_and_email(user.full_name, user.email_address)
        self.users_roles.select_email_invite()
        self.users_roles.click_add()

        user.id = self.users_roles.retrieve_id_from_link(user.full_name)
        self.users_roles.validate_success_message(self.users.messages.msg_success_added_user_invitation)
        self.users_roles.validate_user_data(user)
        # TODO - check email and complete registration

    @pytest.mark.testrail(id=5247)
    @pytest.mark.dependency(depends=["test_add_user_with_custom_password"])
    @pytest.mark.run(order=4)
    def test_last_activity_first_login(self):
        user = decode_data(str(self.users.add[1]))
        # Log in with new user
        self.login.click_logout()
        self.login.simple_login(user.email_address, user.password)
        # Log out and log in with admin
        self.login.click_logout()
        self.login.simple_login(self.data.login.username, self.data.login.password)
        # check if last active record is updated
        self.users_roles.open_page(self.users_overview_url)
        user.last_activity = self.users_roles.check_last_activity(user)
        self.users_roles.check_user_details_last_activity(user)

    @pytest.mark.testrail(id=100)
    @pytest.mark.dependency(depends=["test_add_user_with_email_invitation"])
    @pytest.mark.run(order=5)
    def test_edit_user(self):
        user = decode_data(str(self.users.edit))
        user_to_edit = decode_data(str(self.users.add[2]))

        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.select_user(user_to_edit.full_name)
        self.users_roles.edit_user(user)
        self.users_roles.click_add()

        user.id = self.users_roles.retrieve_id_from_link(user.full_name)
        self.users_roles.validate_success_message(self.users.messages.msg_success_updated_user)
        self.users_roles.validate_user_data(user)
        self.login.click_logout()
        self.login.simple_login(user.email_address, user.password)

    @pytest.mark.testrail(id=103)
    @pytest.mark.run(order=6)
    def test_edit_own_profile(self):
        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.select_user(self.data.login.full_name)
        self.users_roles.validate_hint_message(self.users.messages.msg_hint_edit_own_profile)
        self.users_roles.click_cancel()

    @pytest.mark.testrail(id=99)
    @pytest.mark.run(order=7)
    def test_delete_last_admin(self):
        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.select_user(self.data.login.full_name)
        self.users_roles.delete_last_admin()
        self.users_roles.validate_error_message(self.users.messages.msg_err_cant_delete_last_admin)

    @pytest.mark.run(order=8)
    def test_contact_admin_forget_user(self):
        # Test Contact Admin Not Forget himself
        self.login.open_page(self.data.server_name + self.users.edit_user_details_url + "1")
        self.users_roles.validate_admin_not_forget_user()

    @pytest.mark.dependency(name="test_contact_admin_forget_admin")
    @pytest.mark.run(order=9)
    def test_contact_admin_forget_admin(self):
        user = decode_data(str(self.users.add_admin_user[0]))
        user = decode_data(str(self.users.add_admin_user[0]))
        self.users_roles.open_page(self.data.server_name + self.users.add_user_url)
        self.users_roles.add_name_and_email(user.full_name, user.email_address)
        self.users_roles.insert_manual_password(user.password)
        self.users_roles.add_user_as_admin()
        user.id = self.users_roles.retrieve_id_from_link(user.full_name)

        # Test Contact Admin Forget admin
        self.login.open_page(self.data.server_name + self.users.edit_user_details_url + user.id)
        self.users_roles.validate_admin_forget_user()

    @pytest.mark.dependency(depends=["test_contact_admin_forget_admin"])
    @pytest.mark.run(order=10)
    def test_admin_forget_contact_admin(self):
        #Login as admin
        self.login.click_logout()
        admin_user = self.users.add_admin_user[0]
        self.login.simple_login(admin_user.email_address, admin_user.password)
        # Test admin not forget contact admin
        self.login.open_page(self.data.server_name + self.users.edit_user_details_url + "1")
        self.users_roles.validate_admin_not_forget_user()

    @pytest.mark.dependency(depends=["test_contact_admin_forget_admin"])
    @pytest.mark.run(order=11)
    def test_admin_forget_other_admin_user(self):
        #Login as admin
        self.login.click_logout()
        self.login.simple_login(self.users.add_admin_user[0].email_address, self.users.add_admin_user[0].password)
        user = decode_data(str(self.users.add_admin_user[1]))
        self.users_roles.open_page(self.data.server_name + self.users.add_user_url)
        self.users_roles.add_name_and_email(user.full_name, user.email_address)
        self.users_roles.insert_manual_password(user.password)
        self.users_roles.add_user_as_admin()

        user_id = self.users_roles.retrieve_id_from_link(user.full_name)

        # Test admin forget another admin
        self.login.open_page(self.data.server_name + self.users.edit_user_details_url + user_id)
        self.users_roles.validate_admin_forget_user()

    @pytest.mark.testrail(id=1167)
    @pytest.mark.dependency(name="test_bulk_users_success")
    @pytest.mark.run(order=12)
    def test_bulk_users_success(self):
        users_to_add = self.users.add_multiple.users
        added_users = self.users.add_multiple.result

        self.users_roles.open_page(self.data.server_name + self.users.add_multiple_users_url)
        self.users_roles.insert_users(users_to_add)
        self.users_roles.validate_identified_users(added_users)
        self.users_roles.click_add()
        self.users_roles.wait_to_finish_adding()
        self.users_roles.validate_confirmation_pop_up(self.users.messages.msg_success_added_all_users, added_users)
        self.users_roles.click_confirmation_add()

    @pytest.mark.run(order=9)
    def test_add_multiple_users_validation_no_users(self):
        self.users_roles.open_page(self.data.server_name + self.users.add_multiple_users_url)
        self.users_roles.click_add()
        self.users_roles.validate_error_message_pop_up(self.users.messages.msg_err_users_validation)

    @pytest.mark.testrail(id=1168)
    @pytest.mark.dependency(depends=["test_bulk_users_success"])
    @pytest.mark.run(order=10)
    def test_add_multiple_users_validation_users_existing(self):
        users_to_add = self.users.add_multiple.users

        self.users_roles.open_page(self.data.server_name + self.users.add_multiple_users_url)
        self.users_roles.insert_users(users_to_add)
        time.sleep(3)
        self.users_roles.click_add()
        self.users_roles.validate_error_message_pop_up(self.users.messages.msg_err_users_validation)

    @pytest.mark.run(order=11)
    def test_add_multiple_users_validation_invalid_line_format(self):
        users_to_add = self.users.add_multiple.invalid_users

        self.users_roles.open_page(self.data.server_name + self.users.add_multiple_users_url)
        self.users_roles.insert_users(users_to_add)
        time.sleep(3)
        self.users_roles.click_add()
        self.users_roles.validate_error_message_pop_up(self.users.messages.msg_err_users_invalid_line_format_popup)

    @pytest.mark.testrail(id=1162)
    @pytest.mark.dependency(name="test_add_group_success",
        depends=["test_add_user_with_custom_password",
                 "test_add_user_with_email_invitation",
                 "test_bulk_users_success"])
    @pytest.mark.run(order=12)
    def test_add_group_success(self):
        group_name = self.users.group.add_name

        self.users_roles.open_page(self.data.server_name + self.users.add_group_url)
        self.users_roles.add_group(group_name,3)

    @pytest.mark.testrail(id=1163)
    @pytest.mark.dependency(depends=["test_add_group_success"])
    @pytest.mark.run(order=13)
    def test_edit_group_success(self):
        group_name = self.users.group.edited_group

        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.open_groups_tab()
        self.users_roles.open_group(self.users.group.add_name)
        self.users_roles.edit_group(group_name,5)
        id = self.users_roles.retrieve_id_from_link(group_name)
        self.users_roles.validate_success_message(self.users.messages.msg_success_edited_group)
        self.users_roles.validate_group(id, group_name, 2)

    @pytest.mark.testrail(id=1164)
    @pytest.mark.dependency(depends=["test_add_group_success"])
    @pytest.mark.run(order=14)
    def test_delete_group_success(self):
        group_name = self.users.group.edited_group

        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.open_groups_tab()
        id = self.users_roles.retrieve_id_from_link(group_name)
        self.users_roles.delete_group(id)
        self.users_roles.validate_success_message(self.users.messages.msg_success_deleted_group)

    @pytest.mark.testrail(id=105)
    @pytest.mark.dependency(name='test_add_new_role')
    def test_add_role_new_role(self):
        # Note that not all possible values are valid. You can't
        # have permission to delete an entity but not have permission
        # to add/edit that entity.
        role = decode_data(str(self.users.roles.new_role))
        message = self.users.roles.messages.msg_success_role_added

        self.users_roles.open_page(self.data.server_name + self.users.add_role_url)
        self.users_roles.add_role(role)
        self.users_roles.verify_role(role, message)

    def test_add_role_all_permissions(self):
        role = decode_data(str(self.users.roles.all_permissions))
        message = self.users.roles.messages.msg_success_role_added

        self.users_roles.open_page(self.data.server_name + self.users.add_role_url)
        self.users_roles.add_role(role)
        self.users_roles.verify_role(role, message)

        self.users_roles.delete_role(role.name)

    def test_add_role_no_permissions(self):
        role = decode_data(str(self.users.roles.no_permissions))
        message = self.users.roles.messages.msg_success_role_added

        self.users_roles.open_page(self.data.server_name + self.users.add_role_url)
        self.users_roles.add_role(role)
        self.users_roles.verify_role(role, message)

        self.users_roles.delete_role(role.name)

    @pytest.mark.testrail(id=106)
    @pytest.mark.dependency(name="test_edit_role", depends=['test_add_new_role'])
    def test_edit_role(self):
        role = decode_data(str(self.users.roles.new_role))
        new_permissions = (RolePermissions.RUNS_ADD | RolePermissions.CASES_ADD | RolePermissions.SUITES_ADD).value
        role.permissions = new_permissions
        message = self.users.roles.messages.msg_success_role_edited

        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.open_roles_tab()
        self.users_roles.open_role(role.name)
        self.users_roles.edit_role(role)
        self.users_roles.verify_role(role, message)

    @pytest.mark.dependency(depends=['test_edit_role'])
    def test_delete_role(self):
        role = decode_data(str(self.users.roles.new_role))
        new_permissions = (RolePermissions.RUNS_ADD | RolePermissions.CASES_ADD | RolePermissions.SUITES_ADD).value
        role.permissions = new_permissions
        message = self.users.roles.messages.msg_success_role_deleted

        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.open_roles_tab()
        self.users_roles.delete_role(role.name)
        self.users_roles.validate_success_message(message)

    # Modify test results permission
    @pytest.mark.testrail(id=5840)
    def test_create_role_with_permission_to_modify_test_results_and_assign_role_to_user(self):
        role = decode_data(str(self.users.roles.new_role))
        role.permissions = (RolePermissions.RESULTS_ADD | RolePermissions.RESULTS_MODIFY).value
        user = decode_data(str(self.users.tester_user))
        message = self.users.roles.messages.msg_success_role_added
        updated_user_message = self.users.messages.msg_success_updated_user

        try:
            self.users_roles.open_page(self.data.server_name + self.users.add_role_url)
            self.users_roles.add_role(role)
            self.users_roles.verify_role(role, message)
            self.users_roles.open_page(self.users_overview_url)
            self.users_roles.add_user(user)
            self.users_roles.select_user(self.users.tester_user.full_name)
            self.users_roles.open_access_tab()
            self.users_roles.change_role_for_user(role.name)
            self.users_roles.validate_success_message(updated_user_message)
        finally:
            self.users_roles.open_page(self.users_overview_url)
            self.users_roles.forget_user(self.users.tester_user.full_name)
            self.users_roles.open_page(self.users_overview_url)
            self.users_roles.open_roles_tab()
            self.users_roles.delete_role(role.name)

    @pytest.mark.testrail(id=5668)
    def test_edit_role_and_add_modify_test_results_permission(self):
        role = decode_data(str(self.users.roles.no_permissions))
        edited_role = copy.deepcopy(role)
        edited_role.permissions = (RolePermissions.RUNS_ADD | RolePermissions.CASES_ADD | RolePermissions.SUITES_ADD | RolePermissions.RESULTS_ADD | RolePermissions.RESULTS_MODIFY).value
        message = self.users.roles.messages.msg_success_role_edited

        try:
            self.users_roles.open_page(self.data.server_name + self.users.add_role_url)
            self.users_roles.add_role(role)
            self.users_roles.open_role(role.name)
            self.users_roles.edit_role(edited_role)
            self.users_roles.verify_role(edited_role, message)
        finally:
            self.users_roles.open_page(self.users_overview_url)
            self.users_roles.open_roles_tab()
            self.users_roles.delete_role(edited_role.name)

    @pytest.mark.testrail(id=5669)
    def test_edit_role_and_remove_modify_test_results_permission(self):
        role = decode_data(str(self.users.roles.all_permissions))
        edited_role = copy.deepcopy(role)
        edited_role.permissions = (
                    RolePermissions.RUNS_ADD | RolePermissions.CASES_ADD | RolePermissions.SUITES_ADD).value
        message = self.users.roles.messages.msg_success_role_edited

        try:
            self.users_roles.open_page(self.data.server_name + self.users.add_role_url)
            self.users_roles.add_role(role)
            self.users_roles.open_role(role.name)
            self.users_roles.edit_role(edited_role)
            self.users_roles.verify_role(edited_role, message)
        finally:
            self.users_roles.open_page(self.users_overview_url)
            self.users_roles.open_roles_tab()
            self.users_roles.delete_role(edited_role.name)

    @pytest.mark.testrail(id=5384)
    def test_bulk_edit_screen_checkboxes(self):
        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.check_checkboxes_exist()

    @pytest.mark.testrail(id=5382)
    def test_bulk_edit_button_exists(self):
        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.check_bulk_update_dropdown_is_displayed()

    @pytest.mark.testrail(id=5408)
    def test_remove_user_from_bulk_update_view(self):
        self.users_roles.open_page(self.users_overview_url)
        count = self.users_roles.get_user_count()
        self.users_roles.click_bulk_update_all()
        self.users_roles.remove_users_from_bulk_update(count)
        self.users_roles.click_cancel()

    def test_cancel_bulk_update(self):
        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.click_bulk_update_all()
        self.users_roles.click_cancel()
        self.users_roles.check_page(self.users_overview_url)

    @pytest.mark.testrail(id=5395)
    def test_various_displayed_dropdown(self):
        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.click_bulk_update_all()
        self.users_roles.check_administrator_various_displayed()

    @pytest.mark.testrail(id=5399)
    def test_various_groups_displayed(self):
        user1 = decode_data(str(self.users.add[0]))
        user2 = decode_data(str(self.users.add[1]))
        try:
            self.users_roles.open_page(self.data.server_name + self.users.add_group_url)
            self.users_roles.add_group_with_user(self.users.group.bulk_group_1, [user1.full_name])
            self.users_roles.open_page(self.data.server_name + self.users.add_group_url)
            self.users_roles.add_group_with_user(self.users.group.bulk_group_2, [user2.full_name])
            self.users_roles.open_page(self.users_overview_url)
            self.users_roles.apply_filter('all')
            self.users_roles.click_bulk_update_all()
            self.users_roles.check_groups_various_displayed()
        finally:
            self.users_roles.open_page(self.users_overview_url)
            self.users_roles.open_groups_tab()
            group_id = self.users_roles.retrieve_id_from_link(self.users.group.bulk_group_1)
            group_id2 = self.users_roles.retrieve_id_from_link(self.users.group.bulk_group_2)
            self.users_roles.delete_group(group_id)
            self.users_roles.delete_group(group_id2)
            self.users_roles.open_page(self.users_overview_url)
            self.users_roles.apply_filter('active')

    @pytest.mark.testrail(id=5402)
    def test_confirmation_page_displayed(self):
        try:
            self.users_roles.open_page(self.users_overview_url)
            self.users_roles.apply_filter('all')
            count = self.users_roles.get_user_count()
            self.users_roles.click_bulk_update_all()
            self.users_roles.bulk_edit_email_notification('Off')
            self.users_roles.bulk_save_changes()
            self.users_roles.check_confirmation_page_displayed()
            self.users_roles.check_number_users_displayed_on_button(count)
            self.users_roles.click_cancel()
        finally:
            self.users_roles.open_page(self.users_overview_url)
            self.users_roles.apply_filter('active')

    @pytest.mark.testrail(id=5414)
    def test_bulk_save_changes(self):
        user_to_check = decode_data(str(self.users.add[0]))
        try:
            self.users_roles.open_page(self.users_overview_url)
            self.users_roles.select_users([user_to_check.full_name])
            self.users_roles.click_bulk_update_selected()
            self.users_roles.add_bulk_update_changes(email_notification=self.users.bulk_edit.email_notification,
                                                     locale=self.users.bulk_edit.locale,
                                                     time_zone=self.users.bulk_edit.time_zone,
                                                     language=self.users.bulk_edit.language,
                                                     sso=self.users.bulk_edit.sso, role=self.users.bulk_edit.role,
                                                     is_administrator=self.users.bulk_edit.is_administrator,
                                                     active=self.users.bulk_edit.active)
            self.users_roles.bulk_save_changes()
            self.users_roles.check_confirmation_page_displayed()
            self.users_roles.click_save_changes()
            self.users_roles.open_page(self.users_overview_url)
            self.users_roles.apply_filter('all')
            self.users_roles.select_user(user_to_check.full_name)
            self.users_roles.check_user_updated(email_notification=self.users.bulk_edit.email_notification,
                                                locale=self.users.bulk_edit.locale,
                                                time_zone=self.users.bulk_edit.time_zone,
                                                language=self.users.bulk_edit.language,
                                                sso=self.users.bulk_edit.sso, role=self.users.bulk_edit.role,
                                                is_administrator=self.users.bulk_edit.is_administrator,
                                                active=self.users.bulk_edit.active)
        finally:
            self.users_roles.open_page(self.users_overview_url)
            self.users_roles.apply_filter('active')

    def delete_prepared_data(self):
        self.users_roles.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)
        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.forget_all_added_users(self.users.messages.msg_success_updated_user)

    @pytest.mark.testrail(id=107)
    def test_default_role_deletion(self):
        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.open_roles_tab()
        self.users_roles.check_role_cannot_be_deleted("Lead")


if __name__ == "__main__":
    pytest.main()
