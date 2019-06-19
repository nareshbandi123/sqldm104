import pytest
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from src.locators.administration.users_roles_locators import UsersRolesLocator
from src.locators.general_locators import GeneralLocators
from src.locators.administration.administration_locators import AdministrationLocators
from src.pages.base_element import BasePageElement
from src.pages.base_page import BasePage
from src.models.administration.user import User,Role, RolePermissions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from src.common import decode_data
from typing import Tuple


class UsersRolesPage(BasePage, BasePageElement):

    def add_name_and_email(self, full_name, email):
        self.send_keys_to_element(UsersRolesLocator.full_name, full_name)
        self.send_keys_to_element(UsersRolesLocator.email_address, email)

    def insert_manual_password(self, password):
        manual = self.find_elements_by_locator(UsersRolesLocator.manually_specify_psw)
        if len(manual) != 0:
            self.click_element(UsersRolesLocator.manually_specify_psw)
        self.send_keys_to_element(UsersRolesLocator.password, password)
        self.send_keys_to_element(UsersRolesLocator.confirm_password, password)

    def select_email_invite(self):
        self.click_element(UsersRolesLocator.invite_user)

    def click_add(self):
        self.click_element(UsersRolesLocator.add_user)

    def click_cancel(self):
        self.click_element(GeneralLocators.cancel)

    def click_save_changes(self):
        self.click_element(GeneralLocators.ok)

    def validate_user_data(self, user:User):
        row = self.find_element_by_locator_and_value(By.ID, UsersRolesLocator.cn_users_row + user.id)

        self.validate_nested_element_text(row, UsersRolesLocator.users_full_name, user.full_name)
        self.validate_nested_element_text(row, UsersRolesLocator.users_email_address, user.email_address)
        self.validate_nested_element_text(row, UsersRolesLocator.users_last_active, user.last_activity)
        self.validate_nested_element_text(row, UsersRolesLocator.users_status, user.status)
        self.validate_nested_element_text(row, UsersRolesLocator.users_role, user.role)

    def check_last_activity(self, user:User) -> str:
        user.id = self.retrieve_id_from_link(user.full_name)
        row = self.find_element_by_locator_and_value(By.ID, UsersRolesLocator.cn_users_row + user.id)
        last_active = self.find_nested_element(row, UsersRolesLocator.users_last_active)
        assert (last_active.text != "Never logged in")
        return last_active.text

    def check_user_details_last_activity(self, user: User):
        self.select_user(user.full_name)
        self.click_element(UsersRolesLocator.tab2)
        self.validate_element_text(UsersRolesLocator.last_activity, user.last_activity)

    def select_user(self, name):
        element = self.find_element_by_class_name_from_list(UsersRolesLocator.cn_users_full_name, name)
        element.click()

    def edit_user(self, user: User):
        self.clear_element_data(UsersRolesLocator.full_name)
        self.send_keys_to_element(UsersRolesLocator.full_name, user.full_name)
        self.clear_element_data(UsersRolesLocator.email_address)
        self.send_keys_to_element(UsersRolesLocator.email_address, user.email_address)
        if user.language:
            self.send_keys_to_element(UsersRolesLocator.language, user.language)
        if user.locale:
            self.send_keys_to_element(UsersRolesLocator.locale, user.locale)
        if user.time_zone:
            self.send_keys_to_element(UsersRolesLocator.time_zone, user.time_zone)
        if user.password:
            self.send_keys_to_element(UsersRolesLocator.password, user.password)
        if user.password:
            self.send_keys_to_element(UsersRolesLocator.confirm_password, user.password)

    def set_as_inactive(self):
        self.click_element(UsersRolesLocator.tab2)
        active = self.get_attribute_value_from_element(self.find_element_by_locator(UsersRolesLocator.is_active), 'checked')
        if active is not None:
            self.click_element(UsersRolesLocator.is_active)

    def delete_last_admin(self):
        self.click_element(UsersRolesLocator.tab2)
        self.click_element(UsersRolesLocator.is_active)
        self.click_element(UsersRolesLocator.add_user)

    def add_user_as_admin(self):
        self.click_element(GeneralLocators.tab2)
        self.click_element(UsersRolesLocator.is_admin)
        self.click_element(UsersRolesLocator.add_user)

    def clear_name_and_email(self):
        self.clear_element_data(UsersRolesLocator.full_name)
        self.clear_element_data(UsersRolesLocator.email_address)

    def insert_users(self, users:str):
        self.send_keys_to_element(UsersRolesLocator.multiple_users, users)

    def validate_identified_users(self, users:str):
        preview = self.find_element_by_locator(UsersRolesLocator.preview)
        id = 1
        for item in users:
            user = decode_data(str(item))
            user_preview = preview.find_element_by_id(UsersRolesLocator.user_preview + str(id))
            assert (user_preview.find_element(*UsersRolesLocator.user_preview_id).text == str(id))
            assert (user_preview.find_element(*UsersRolesLocator.user_preview_name).text == user.full_name)
            assert (user_preview.find_element(*UsersRolesLocator.user_preview_email).text == user.email_address)
            assert (user_preview.find_element(*UsersRolesLocator.user_preview_new).text == "New")
            id = id + 1

    def validate_confirmation_pop_up(self, message:str, users:str):
        self.validate_element_text(UsersRolesLocator.add_users_message_success, message)
        self.validate_added_users(users)

    def validate_added_users(self, users: str):
        add_users_table = self.find_element_by_locator(UsersRolesLocator.add_users_table)
        preview = add_users_table.find_element(*UsersRolesLocator.preview)
        id = 1
        for item in users:
            user = decode_data(str(item))
            user_preview = preview.find_element_by_id(UsersRolesLocator.user_dialog + str(id))
            assert (user_preview.find_element(*UsersRolesLocator.user_preview_id).text == str(id))
            assert (user_preview.find_element(*UsersRolesLocator.user_preview_name).text == user.full_name)
            assert (user_preview.find_element(*UsersRolesLocator.user_preview_email).text == user.email_address)
            assert (user_preview.find_element(*UsersRolesLocator.user_preview_new).text == "Success")
            id = id + 1

    def wait_to_finish_adding(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(ec.visibility_of_element_located(UsersRolesLocator.add_users_message_success))

    def click_confirmation_add(self):
        add_users_form = self.find_element_by_locator(UsersRolesLocator.add_users_form)
        add_users_form.find_element(*UsersRolesLocator.add_users_confirm).click()

    def validate_error_message_pop_up(self, message):
        dialog = self.driver.find_element(*GeneralLocators.dialog)
        dialog_message = dialog.find_element(*GeneralLocators.dialog_message)
        assert dialog_message.text == message

    def check_validation_message(self, message):
        rows = self.driver.find_elements_by_class_name("odd")
        id = 1
        for row in rows:
            assert (row.find_element(*UsersRolesLocator.user_preview_id).text == str(id))
            assert (row.find_element(*UsersRolesLocator.user_preview_error).text == message)

    def open_groups_tab(self):
        self.click_element(UsersRolesLocator.tab2)

    def add_group(self, name: str, count: int):
        self.send_keys_to_element(UsersRolesLocator.group_name, name)
        self.check_users_on_list(count)
        self.click_element(UsersRolesLocator.add_group)

    def check_users_on_list(self, count):
        self.click_count_of_elements_on_list(UsersRolesLocator.group_names, count)

    def open_group(self, group_name):
        self.find_element_by_locator_and_value(By.LINK_TEXT, group_name).click()

    def edit_group(self, group_name:str, count:int):
        self.clear_element_data(UsersRolesLocator.group_name)
        self.send_keys_to_element(UsersRolesLocator.group_name, group_name)
        self.check_users_on_list(count)
        self.click_element(UsersRolesLocator.add_group)

    def validate_group(self, id, group_name, count):
        try:
            row = self.find_element_by_locator_and_value(By.ID, UsersRolesLocator.id_group_row + id)
            group_name = row.find_element_by_link_text(group_name)
            number_of_users = row.find_element_by_xpath("td[2]")
            assert (number_of_users.text == str(count))
        except TimeoutException:
            pytest.fail("Element not found")
        except NoSuchElementException:
            pytest.fail("Element not found")

    def delete_group(self, id):
        try:
            row = self.find_element_by_locator_and_value(By.ID, UsersRolesLocator.id_group_row + id)
            row.find_element_by_xpath("td[4]/a").click()
            self.confirm_popup_delete()

        except TimeoutException:
            pytest.fail("Element not found")
        except NoSuchElementException:
            pytest.fail("Element not found")

    def open_roles_tab(self):
        self.wait_for_element_to_be_visible(UsersRolesLocator.tab3)
        self.wait_for_element_to_be_clickable(UsersRolesLocator.tab3)
        self.click_element(UsersRolesLocator.tab3)

    def verify_if_role_exists(self, role_name):
        return self.validate_element_visibility((By.XPATH, UsersRolesLocator.get_role_by_name(role_name)))

    def add_role(self, role:Role):
        self.send_keys_to_element(UsersRolesLocator.full_name, role.name)
        if role.is_default:
            # Note that changing the default role is a bad idea for tests
            # unless they restore the original default afterwards.
            self.click_element(UsersRolesLocator.is_default_role)

        role_flags = RolePermissions(role.permissions)
        if role_flags & RolePermissions.ATTACHMENTS_ADD:
            self.click_element(UsersRolesLocator.permission_attachments_addedit)
        if role_flags & RolePermissions.ATTACHMENTS_DEL:
            self.click_element(UsersRolesLocator.permission_attachments_delete)
        if role_flags & RolePermissions.CASES_ADD:
            self.click_element(UsersRolesLocator.permission_cases_addedit)
        if role_flags & RolePermissions.CASES_DEL:
            self.click_element(UsersRolesLocator.permission_cases_delete)
        if role_flags & RolePermissions.CONFIGS_ADD:
            self.click_element(UsersRolesLocator.permission_configs_addedit)
        if role_flags & RolePermissions.CONFIGS_DEL:
            self.click_element(UsersRolesLocator.permission_configs_delete)
        if role_flags & RolePermissions.MILESTONES_ADD:
            self.click_element(UsersRolesLocator.permission_milestones_addedit)
        if role_flags & RolePermissions.MILESTONES_DEL:
            self.click_element(UsersRolesLocator.permission_milestones_delete)
        if role_flags & RolePermissions.RUNS_ADD:
            self.click_element(UsersRolesLocator.permission_runs_addedit)
        if role_flags & RolePermissions.RUNS_DEL:
            self.click_element(UsersRolesLocator.permission_runs_delete)
        if role_flags & RolePermissions.RUNS_CLOSE:
            self.click_element(UsersRolesLocator.permission_runs_close)
        if role_flags & RolePermissions.RUNS_CLOSED_DEL:
            self.click_element(UsersRolesLocator.permission_runs_closed_delete)
        if role_flags & RolePermissions.REPORTS_ADD:
            self.click_element(UsersRolesLocator.permission_reports_addedit)
        if role_flags & RolePermissions.REPORTS_DEL:
            self.click_element(UsersRolesLocator.permission_reports_delete)
        if role_flags & RolePermissions.SCHEDULED_REPORTS_ADD:
            self.click_element(UsersRolesLocator.permission_reports_jobs_addedit)
        if role_flags & RolePermissions.SCHEDULED_REPORTS_DEL:
            self.click_element(UsersRolesLocator.permission_reports_jobs_delete)
        if role_flags & RolePermissions.SUITES_ADD:
            self.click_element(UsersRolesLocator.permission_suites_addedit)
        if role_flags & RolePermissions.SUITES_DEL:
            self.click_element(UsersRolesLocator.permission_suites_delete)
        if role_flags & RolePermissions.RESULTS_ADD:
            self.click_element(UsersRolesLocator.permission_results_addedit)
        if role_flags & RolePermissions.RESULTS_MODIFY:
            self.click_element(UsersRolesLocator.permission_results_modify)

        self.click_element(GeneralLocators.add)

    def edit_role(self, role: Role):
        def check_and_modify_checkbox(locator: Tuple[str, str], expected_value: bool):
            expected_value = bool(expected_value)
            element = self.find_element_by_locator(locator)
            if element.is_selected() != expected_value:
                element.click()

        self.clear_element_data(UsersRolesLocator.full_name)
        self.send_keys_to_element(UsersRolesLocator.full_name, role.name)

        role_flags = RolePermissions(role.permissions)

        if self.validate_element_visibility(UsersRolesLocator.is_default_role):
            check_and_modify_checkbox(UsersRolesLocator.is_default_role, role.is_default)

        check_and_modify_checkbox(UsersRolesLocator.permission_attachments_addedit,
                                  role_flags & RolePermissions.ATTACHMENTS_ADD)
        check_and_modify_checkbox(UsersRolesLocator.permission_attachments_delete,
                                  role_flags & RolePermissions.ATTACHMENTS_DEL)
        check_and_modify_checkbox(UsersRolesLocator.permission_cases_addedit,
                                  role_flags & RolePermissions.CASES_ADD)
        check_and_modify_checkbox(UsersRolesLocator.permission_cases_delete,
                                  role_flags & RolePermissions.CASES_DEL)
        check_and_modify_checkbox(UsersRolesLocator.permission_configs_addedit,
                                  role_flags & RolePermissions.CONFIGS_ADD)
        check_and_modify_checkbox(UsersRolesLocator.permission_configs_delete,
                                  role_flags & RolePermissions.CONFIGS_DEL)
        check_and_modify_checkbox(UsersRolesLocator.permission_milestones_addedit,
                                  role_flags & RolePermissions.MILESTONES_ADD)
        check_and_modify_checkbox(UsersRolesLocator.permission_milestones_delete,
                                  role_flags & RolePermissions.MILESTONES_DEL)
        check_and_modify_checkbox(UsersRolesLocator.permission_runs_addedit,
                                  role_flags & RolePermissions.RUNS_ADD)
        check_and_modify_checkbox(UsersRolesLocator.permission_runs_delete,
                                  role_flags & RolePermissions.RUNS_DEL)
        check_and_modify_checkbox(UsersRolesLocator.permission_runs_close,
                                  role_flags & RolePermissions.RUNS_CLOSE)
        check_and_modify_checkbox(UsersRolesLocator.permission_runs_closed_delete,
                                  role_flags & RolePermissions.RUNS_CLOSED_DEL)
        check_and_modify_checkbox(UsersRolesLocator.permission_reports_addedit,
                                  role_flags & RolePermissions.REPORTS_ADD)
        check_and_modify_checkbox(UsersRolesLocator.permission_reports_delete,
                                  role_flags & RolePermissions.REPORTS_DEL)
        check_and_modify_checkbox(UsersRolesLocator.permission_reports_jobs_addedit,
                                  role_flags & RolePermissions.SCHEDULED_REPORTS_ADD)
        check_and_modify_checkbox(UsersRolesLocator.permission_reports_jobs_delete,
                                  role_flags & RolePermissions.SCHEDULED_REPORTS_DEL)
        check_and_modify_checkbox(UsersRolesLocator.permission_suites_addedit,
                                  role_flags & RolePermissions.SUITES_ADD)
        check_and_modify_checkbox(UsersRolesLocator.permission_suites_delete,
                                  role_flags & RolePermissions.SUITES_DEL)
        check_and_modify_checkbox(UsersRolesLocator.permission_results_addedit,
                                  role_flags & RolePermissions.RESULTS_ADD)
        check_and_modify_checkbox(UsersRolesLocator.permission_results_modify,
                                  role_flags & RolePermissions.RESULTS_MODIFY)

        self.click_element(GeneralLocators.add)

    def check_role(self, role: Role):
        if role.is_default == 0:
            self.assert_role_value(UsersRolesLocator.is_default_role, role.is_default)
        else:
            self.check_element_not_exists(UsersRolesLocator.is_default_role)

        role_flags = RolePermissions(role.permissions)

        self.assert_role_value(UsersRolesLocator.permission_attachments_addedit,
                               bool(role_flags & RolePermissions.ATTACHMENTS_ADD))
        self.assert_role_value(UsersRolesLocator.permission_attachments_delete,
                               bool(role_flags & RolePermissions.ATTACHMENTS_DEL))
        self.assert_role_value(UsersRolesLocator.permission_cases_addedit,
                               bool(role_flags & RolePermissions.CASES_ADD))
        self.assert_role_value(UsersRolesLocator.permission_cases_delete,
                               bool(role_flags & RolePermissions.CASES_DEL))
        self.assert_role_value(UsersRolesLocator.permission_configs_addedit,
                               bool(role_flags & RolePermissions.CONFIGS_ADD))
        self.assert_role_value(UsersRolesLocator.permission_configs_delete,
                               bool(role_flags & RolePermissions.CONFIGS_DEL))
        self.assert_role_value(UsersRolesLocator.permission_milestones_addedit,
                               bool(role_flags & RolePermissions.MILESTONES_ADD))
        self.assert_role_value(UsersRolesLocator.permission_milestones_delete,
                               bool(role_flags & RolePermissions.MILESTONES_DEL))
        self.assert_role_value(UsersRolesLocator.permission_runs_addedit,
                               bool(role_flags & RolePermissions.RUNS_ADD))
        self.assert_role_value(UsersRolesLocator.permission_runs_delete,
                               bool(role_flags & RolePermissions.RUNS_DEL))
        self.assert_role_value(UsersRolesLocator.permission_runs_close,
                               bool(role_flags & RolePermissions.RUNS_CLOSE))
        self.assert_role_value(UsersRolesLocator.permission_runs_closed_delete,
                               bool(role_flags & RolePermissions.RUNS_CLOSED_DEL))
        self.assert_role_value(UsersRolesLocator.permission_reports_addedit,
                               bool(role_flags & RolePermissions.REPORTS_ADD))
        self.assert_role_value(UsersRolesLocator.permission_reports_delete,
                               bool(role_flags & RolePermissions.REPORTS_DEL))
        self.assert_role_value(UsersRolesLocator.permission_suites_addedit,
                               bool(role_flags & RolePermissions.SUITES_ADD))
        self.assert_role_value(UsersRolesLocator.permission_suites_delete,
                               bool(role_flags & RolePermissions.SUITES_DEL))
        self.assert_role_value(UsersRolesLocator.permission_results_addedit,
                               bool(role_flags & RolePermissions.RESULTS_ADD))
        self.assert_role_value(UsersRolesLocator.permission_results_modify,
                               bool(role_flags & RolePermissions.RESULTS_MODIFY))

    def assert_role_value(self, locator: Tuple[str,str], expected_value: bool):
        element = self.find_element_by_locator(locator)
        assert element.is_selected() == expected_value

    def open_role(self, role_name: str):
        role = self.find_element_by_locator_and_value(By.XPATH, UsersRolesLocator.get_role_by_name(role_name))
        role.click()

    def delete_role(self, role_name:str):
        try:
            role = self.find_element_by_locator_and_value(By.XPATH, UsersRolesLocator.get_role_by_name(role_name))
            role_row = self.get_grandparent_element(role)
            role_row.find_element_by_xpath("td[3]/a").click()
            self.confirm_popup_delete()
        except TimeoutException:
            pytest.fail("Element not found")
        except NoSuchElementException:
            pytest.fail("Element not found")

    def check_role_cannot_be_deleted(self, role_name):
        role = self.find_element_by_locator_and_value(By.XPATH, "//span[contains(., '{}')]".format(role_name))
        role_row = self.get_grandparent_element(role)
        delete_cell = role_row.find_element_by_xpath("td[3]")
        # Assert there is no delete link in this row
        assert len(delete_cell.find_elements_by_tag_name('a')) == 0

    def verify_role(self, role, message=None):
        if message:
            self.validate_element_text(GeneralLocators.message_success, message)
        self.open_role(role.name)
        self.check_role(role)
        self.click_element(GeneralLocators.cancel)

    def setEmailNotification(self, value):
        value = value.lower()
        self.select_item_from_dropdown(UsersRolesLocator.bulk_email_notifications, value=value)

    def enable_sso_user(self, username):
        self.select_user(username)
        if self.find_element_by_locator(UsersRolesLocator.sso_checkbox).get_attribute('checked') is None:
            self.click_element(UsersRolesLocator.sso_checkbox)
        self.click_element(UsersRolesLocator.add_user)

    def disable_sso_user(self, username):
        self.select_user(username)
        if self.find_element_by_locator(UsersRolesLocator.sso_checkbox).get_attribute('checked') == 'true':
            self.click_element(UsersRolesLocator.sso_checkbox)
        self.click_element(UsersRolesLocator.add_user)

    def add_user(self, user: User) -> int:
        if self.check_user_exists(user.full_name) is False:
            self.click_add_user()
            self.send_keys_to_element(UsersRolesLocator.full_name, user.full_name)
            self.send_keys_to_element(UsersRolesLocator.email_address, user.email_address)
            self.insert_manual_password(user.password)
            self.click_element(UsersRolesLocator.add_user)
            self.check_success_message_displayed()
        user_id = self.retrieve_id_from_link(user.full_name)
        return user_id

    def click_add_user(self):
        self.click_element(UsersRolesLocator.add_user_button)

    def check_success_message_displayed(self):
        assert self.find_element_by_locator(UsersRolesLocator.message_success).is_displayed()

    def check_user_exists(self, username):
        try:
            if self.find_element_by_class_name_from_list(UsersRolesLocator.cn_users_full_name, username) is not None:
                return True
            else:
                return False
        except NoSuchElementException:
            return False
        except TimeoutException:
            return False

    def check_sso_checkbox_not_shown(self):
        self.driver.implicitly_wait(1)
        self.check_element_not_exists(UsersRolesLocator.sso_checkbox)

    def check_email_field_disabled(self):
        self.driver.implicitly_wait(1)
        attr = self.get_attribute_value_from_element(self.find_element_by_locator(UsersRolesLocator.email_address), 'class')
        assert 'disabled' in attr

    def check_password_field_not_displayed(self):
        self.driver.implicitly_wait(1)
        self.check_element_not_exists(UsersRolesLocator.password)
        self.check_element_not_exists(UsersRolesLocator.confirm_password)

    def check_users_sso_local(self):
        try:
            elements = self.driver.find_elements_by_class_name('logintype')
            for list_item in elements:
                if list_item.get_attribute('title') == 'Local':
                    continue
                else:
                    pytest.xfail("User login type is SSO when it should be Local")
        except NoSuchElementException:
            pytest.xfail("Element not found")
        except TimeoutException:
            pytest.xfail("Element not found")

    def check_user_login_type_is_sso(self, username):
        self.select_user(username)
        assert self.get_attribute_value_from_element(self.find_element_by_locator(UsersRolesLocator.sso_checkbox), 'checked')

    def check_checkboxes_exist(self):
        self.check_element_is_visible(UsersRolesLocator.checkbox_selectall)
        assert self.find_elements_by_locator(UsersRolesLocator.checkbox_user) is not None

    def check_bulk_update_dropdown_is_displayed(self):
        self.check_element_is_visible(UsersRolesLocator.edit_bulk_dropdown)
        self.click_element(UsersRolesLocator.edit_bulk_dropdown)
        self.check_element_is_visible(UsersRolesLocator.edit_selected)
        self.check_element_is_visible(UsersRolesLocator.edit_all)

    def click_bulk_update_selected(self):
        self.click_element(UsersRolesLocator.edit_bulk_dropdown)
        self.click_element(UsersRolesLocator.edit_selected)

    def click_bulk_update_all(self):
        self.click_element(UsersRolesLocator.edit_bulk_dropdown)
        self.click_element(UsersRolesLocator.edit_all)

    def remove_users_from_bulk_update(self, count: int):
        self.wait_for_element_to_be_visible(GeneralLocators.cancel)
        self.click_count_of_elements_on_list(UsersRolesLocator.bulk_user_delete, count)

    def check_groups_various_displayed(self):
        try:
            self.wait_for_element_to_be_visible(UsersRolesLocator.groups_various)
            element = self.find_element_by_locator(UsersRolesLocator.groups_various)
            assert element.text == '[various]'
        except NoSuchElementException:
            pytest.xfail("Various not displayed")
        except TimeoutException:
            pytest.xfail("Various not displayed")

    def check_administrator_various_displayed(self):
        self.wait_for_element_to_be_visible(GeneralLocators.cancel)
        self.validate_selected_option_text_on_element(UsersRolesLocator.bulk_is_administrator, '[various]')

    def bulk_edit_email_notification(self, value):
        self.wait_for_page_load(10)
        self.select_item_from_dropdown(UsersRolesLocator.bulk_email_notifications, visible_text=value)

    def check_confirmation_page_displayed(self):
        self.check_element_is_visible(UsersRolesLocator.review_modal)

    def check_number_users_displayed_on_button(self, count:int):
        if 'Yes, update all '+ str(count) in self.find_element_by_locator(UsersRolesLocator.review_modal_button_ok).text:
            result = True
        assert result
        confirmation_dialog = self.find_element_by_locator(UsersRolesLocator.review_modal)
        self.click_nested_element(confirmation_dialog, UsersRolesLocator.bulk_cancel)

    def bulk_save_changes(self):
        self.click_element(UsersRolesLocator.bulk_save_changes)

    def forget_user(self, username):
        self.select_user(username)
        self.click_element(UsersRolesLocator.forget_user)
        self.confirm_popup_delete()

    def validate_admin_not_forget_user(self):
        forget_user = self.validate_element_visibility(AdministrationLocators.forget_user)
        assert not forget_user

    def validate_admin_forget_user(self):
        forget_user = self.validate_element_visibility(AdministrationLocators.forget_user)
        assert forget_user

    def get_user_count(self):
        existing_users = self.find_elements_by_locator(UsersRolesLocator.checkbox_user)
        return len(existing_users)

    def forget_all_added_users(self, message:str):
        users = [self.get_attribute_value_from_element(user, "id") for user in self.find_elements_by_locator(UsersRolesLocator.users)]
        for user in users:
            user_id = self.retrieve_id_from_string(user)
            if user_id is not '1':
                user = self.find_element_by_locator((By.ID, user))
                self.click_nested_element(user, UsersRolesLocator.users_name)
                self.click_element(UsersRolesLocator.forget_user)
                self.confirm_popup_delete()
                self.click_element(GeneralLocators.ok)
                self.validate_success_message(message)

    def add_group_with_user(self, name, users):
        self.send_keys_to_element(UsersRolesLocator.group_name, name)
        self.add_users_to_group(users)
        self.click_element(UsersRolesLocator.add_group)

    def add_users_to_group(self, users):
        for i in users:
            locator = (By.XPATH, UsersRolesLocator.get_user_xpath(i))
            element = self.find_element_by_locator(locator)
            element.click()

    def select_users(self, users):
        for i in users:
            user_id = self.retrieve_id_from_link(i)
            self.find_element_by_attribute(UsersRolesLocator.checkbox_user, 'value', user_id).click()

    def add_bulk_update_changes(self, email_notification='On', language='Use application default', locale='Use application default',
                                time_zone='Use application default', sso='Off', role='Lead', active='Active',
                                is_administrator='Yes'):
        self.wait_for_page_load(10)
        try:
            self.select_item_from_dropdown(UsersRolesLocator.bulk_email_notifications, visible_text=email_notification)
            self.select_item_from_dropdown(UsersRolesLocator.bulk_language, visible_text=language)
            self.select_item_from_dropdown(UsersRolesLocator.bulk_locale, visible_text=locale)
            self.select_item_from_dropdown(UsersRolesLocator.bulk_timezone, visible_text=time_zone)
            try:
                Select(self.find_element_by_locator(UsersRolesLocator.bulk_sso)).select_by_visible_text(sso)
            finally:
                self.select_item_from_dropdown(UsersRolesLocator.bulk_role, visible_text=role)
                self.select_item_from_dropdown(UsersRolesLocator.bulk_status, visible_text=active)
                self.select_item_from_dropdown(UsersRolesLocator.bulk_is_administrator, visible_text=is_administrator)
        except:
            pytest.fail("Selecting item from dropdown failed")

    def check_user_updated(self, email_notification='On', language='Use application default', locale='Use application default',
                           time_zone='Use application default', sso='Off', role='Lead', active='Active',
                           is_administrator='Yes'):
        state = {'On': 'true', 'Off': None, 'Yes': 'true', 'No': None, 'Active': 'true', 'Inactive': None}
        assert self.get_attribute_value_from_element(self.find_element_by_locator(UsersRolesLocator.email_notifications), 'checked') == state[email_notification]
        self.validate_selected_option_text_on_element(UsersRolesLocator.language, language)
        self.validate_selected_option_text_on_element(UsersRolesLocator.locale, locale)
        self.validate_selected_option_text_on_element(UsersRolesLocator.time_zone, time_zone)
        assert self.get_attribute_value_from_element(self.find_element_by_locator(UsersRolesLocator.sso_checkbox), 'checked') == state[sso]
        self.click_element(UsersRolesLocator.tab2)
        self.validate_selected_option_text_on_element(UsersRolesLocator.role_id, role)
        assert self.get_attribute_value_from_element(self.find_element_by_locator(UsersRolesLocator.is_active), 'checked') == state[active]
        assert self.get_attribute_value_from_element(self.find_element_by_locator(UsersRolesLocator.is_admin), 'checked') == state[is_administrator]

    def apply_filter(self, filter):
        try:
            self.select_option_value_on_element(UsersRolesLocator.filter_users, filter)
            self.validate_selected_option_value_on_element(UsersRolesLocator.filter_users, filter)
        except:
            pytest.fail("Selecting item from dropdown failed")

    def check_sso_checkbox_state(self, state):
        if state == 'enabled':
            assert 'disabled' not in self.get_attribute_value_from_element(
                self.get_parent_element(self.get_parent_element(self.find_element_by_locator(UsersRolesLocator.sso_checkbox))), 'class')
        else:
            assert 'disabled' in self.get_attribute_value_from_element(
                self.get_parent_element(self.get_parent_element(self.find_element_by_locator(UsersRolesLocator.sso_checkbox))), 'class')

    def check_sso_checkbox_value(self, checked):
        if checked:
            assert self.get_attribute_value_from_element(
                self.find_element_by_locator(UsersRolesLocator.sso_checkbox), 'checked')
        else:
            assert not self.get_attribute_value_from_element(
                self.find_element_by_locator(UsersRolesLocator.sso_checkbox), 'checked')

    def click_sso_checkbox(self):
        self.click_element(UsersRolesLocator.sso_checkbox)

    def add_multiple_users(self, users_to_add, added_users, message):
        self.insert_users(users_to_add)
        self.validate_identified_users(added_users)
        self.click_add()
        self.wait_to_finish_adding()
        self.validate_confirmation_pop_up(message, added_users)
        self.click_confirmation_add()

    def fake_edit_user(self, full_name):
        self.select_user(full_name)
        self.click_add()

    def open_access_tab(self):
        self.click_element(UsersRolesLocator.tab2)

    def change_role_for_user(self, role_name):
        role_select = Select(self.find_element_by_locator(UsersRolesLocator.role_id))
        role_select.select_by_visible_text(role_name)
        self.click_element(UsersRolesLocator.add_user)
