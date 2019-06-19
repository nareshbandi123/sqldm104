import random
import string
from collections import namedtuple
import pytest
import time

from src.test_cases.base_test import BaseTest
from src.common import read_config
from src.pages.administration import customizations_page as customizations


UI_SCRIPT_TEMPLATE = """name: {}
description: A test script
author: Gurock Software
version: 1.0
includes: ^dashboard
excludes:

js:
$(document).ready(
    function() {{
            alert('Test Script');
    }}
);

css:
div.some-class {{
}}"""


class TestCustomizations(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.customizations = read_config('../config/customizations.json')
        cls.customizations_page = customizations.CustomizationsPage(cls.driver)

        cls.setup_database(cls.customizations)

    def setup_method(self):
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)

    def teardown_method(self):
        self.driver.delete_all_cookies()

    def teardown_class(cls):
        cls.teardown_database()
        super().teardown_class()

    @pytest.mark.testrail(id=110)
    @pytest.mark.dependency(name="test_add_case_type")
    def test_add_case_type(self):
        add_case_type_url = (self.data.server_name + self.customizations.add_case_type_url)
        self.customizations_page.open_page(add_case_type_url)
        new_case_type_name = self.customizations.add.new_case_type_name

        self.customizations_page.new_case_type_name(new_case_type_name)
        self.customizations_page.check_page(self.customizations.overview_url)
        self.customizations_page.validate_add_case_type_success(self.customizations.messages.msg_successfully_added_case_type)
        self.customizations_page.check_add_case_type_name(new_case_type_name)

    def test_add_case_type_missing_name(self):
        add_case_type_url = (self.data.server_name + self.customizations.add_case_type_url)
        self.customizations_page.open_page(add_case_type_url)
        self.customizations_page.new_case_type_name("")
        self.customizations_page.validate_add_case_type_missing_name(self.customizations.messages.msg_case_type_missing_name)
        self.customizations_page.check_page(add_case_type_url)

    @pytest.mark.testrail(id=111)
    @pytest.mark.dependency(name="test_edit_case_type", depends=["test_add_case_type"])
    def test_edit_case_type(self):
        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)

        case_type_name = self.customizations.add.new_case_type_name
        case_type_new_name = self.customizations.add.edit_case_type_name
        self.customizations_page.edit_case_type(case_type_name, case_type_new_name)
        self.customizations_page.check_page(self.customizations.overview_url)
        self.customizations_page.validate_add_case_type_success(self.customizations.messages.msg_case_type_updated)
        self.customizations_page.check_add_case_type_name(case_type_new_name)

    @pytest.mark.dependency(depends=["test_add_case_type", "test_edit_case_type"])
    def test_delete_case_type(self):
        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        case_type_name = self.customizations.add.edit_case_type_name
        self.customizations_page.delete_case_type(case_type_name)
        self.customizations_page.check_page(self.customizations.overview_url)
        self.customizations_page.validate_case_type_deleted(self.customizations.messages.msg_case_type_deleted)

    def test_custom_field_required_fields(self):
        self.customizations_page.open_page(self.data.server_name + self.customizations.add_custom_field_url)
        message = self.customizations.messages.msg_custom_field_missing_fields
        self.customizations_page.validate_custom_field_required_fields(message)

    @pytest.mark.testrail(ids=[117, 118, 119, 120, 121, 123, 124, 125, 126, 127, 879])
    # Note that "Steps" is missing as you can't create a new steps field
    @pytest.mark.parametrize('field_type',
        ["Checkbox", "Date", "Dropdown", "Integer", "Milestone", "Multi-select",
         "String", "Text", "Url (Link)", "User"])
    @pytest.mark.parametrize('field_kind', ["custom", "result"])
    def test_add_custom_and_result_field(self, field_type, field_kind):
        if field_kind == 'custom':
            add_url = self.customizations.add_result_field_url
        else:
            add_url = self.customizations.add_custom_field_url

        ts = int(time.time())
        label = "Field Label {}".format(ts)
        description = self.customizations.custom_field.description
        custom_str = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
        system_name = "custom_yourock_{}".format(custom_str)

        self.customizations_page.open_page(self.data.server_name + add_url)
        self.customizations_page.custom_field_add_text_fields(label, system_name, description)

        added_message = self.customizations.messages.msg_custom_field_added
        self.customizations_page.select_custom_field_type(field_type, added_message)
        self.customizations_page.check_page(self.customizations.overview_url)
        self.customizations_page.check_custom_field(label, system_name, description, field_type)

        deleted_message = self.customizations.messages.msg_custom_field_deleted
        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.delete_custom_field(label, deleted_message)

    @pytest.mark.testrail(id=128)
    def test_edit_custom_field(self):
        ts = int(time.time())
        original_label = "Original Field Label {}".format(ts)
        original_description = self.customizations.custom_field.description
        edited_label = "Edited Field Label {}".format(ts)
        edited_description = self.customizations.custom_field.edited_description
        edited_msg = self.customizations.messages.msg_custom_field_edited
        field_type = self.customizations.custom_field.edited_type
        custom_str = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
        system_name = "custom_yourock_{}".format(custom_str)

        self.customizations_page.open_page(self.data.server_name + self.customizations.add_custom_field_url)
        self.customizations_page.custom_field_add_text_fields(original_label, system_name, original_description)

        added_message = self.customizations.messages.msg_custom_field_added
        self.customizations_page.select_custom_field_type(field_type, added_message)
        self.customizations_page.check_page(self.customizations.overview_url)

        self.customizations_page.edit_custom_field(original_label, edited_label, edited_description, edited_msg)
        self.customizations_page.check_page(self.customizations.overview_url)
        self.customizations_page.check_custom_field(edited_label, system_name, edited_description, field_type)
        self.customizations_page.check_template_fields()

        deleted_message = self.customizations.messages.msg_custom_field_deleted
        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.delete_custom_field(edited_label, deleted_message)

    def test_edit_result_field(self):
        ts = int(time.time())
        original_label = "Original Result Field Label {}".format(ts)
        original_description = self.customizations.custom_field.description
        edited_label = "Edited Result Field Label {}".format(ts)
        edited_description = self.customizations.custom_field.edited_description
        edited_msg = self.customizations.messages.msg_custom_field_edited
        field_type = self.customizations.custom_field.edited_type
        custom_str = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
        system_name = "custom_yourock_{}".format(custom_str)

        self.customizations_page.open_page(self.data.server_name + self.customizations.add_result_field_url)
        self.customizations_page.custom_field_add_text_fields(original_label, system_name, original_description)

        added_message = self.customizations.messages.msg_custom_field_added
        self.customizations_page.select_custom_field_type(field_type, added_message)
        self.customizations_page.check_page(self.customizations.overview_url)

        self.customizations_page.edit_custom_field(original_label, edited_label, edited_description, edited_msg)
        self.customizations_page.check_page(self.customizations.overview_url)
        self.customizations_page.check_custom_field(edited_label, system_name, edited_description, field_type)
        self.customizations_page.check_template_fields()

        deleted_message = self.customizations.messages.msg_custom_field_deleted
        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.delete_custom_field(edited_label, deleted_message)

    def test_add_priority_required_field(self):
        self.customizations_page.open_page(self.data.server_name + self.customizations.add_priority_url)
        message = self.customizations.messages.msg_priority_missing_field
        self.customizations_page.validate_priority_required_field(message)

    @pytest.mark.testrail(id=134)
    def test_add_priority(self):
        name = self.customizations.add.new_priority_name
        abbreviation = self.customizations.add.new_priority_abbreviation
        added_message = self.customizations.messages.msg_priority_added

        self.customizations_page.open_page(self.data.server_name + self.customizations.add_priority_url)
        self.customizations_page.add_priority(name, abbreviation, added_message)
        self.customizations_page.check_page(self.customizations.overview_url)
        self.customizations_page.check_priority(name, abbreviation)

        deleted_message = self.customizations.messages.msg_priority_deleted
        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.delete_priority(name, deleted_message)

    @pytest.mark.testrail(id=135)
    def test_edit_priority(self):
        name = self.customizations.add.new_priority_name
        abbreviation = self.customizations.add.new_priority_abbreviation
        added_message = self.customizations.messages.msg_priority_added
        edited_message = self.customizations.messages.msg_priority_edited
        edit_name = self.customizations.add.edit_priority_name
        edit_abbreviation = self.customizations.add.edit_priority_abbreviation

        self.customizations_page.open_page(self.data.server_name + self.customizations.add_priority_url)
        self.customizations_page.add_priority(name, abbreviation, added_message)
        self.customizations_page.check_page(self.customizations.overview_url)

        self.customizations_page.edit_priority(name, edit_name, edit_abbreviation, edited_message)
        self.customizations_page.check_priority(edit_name, edit_abbreviation)

        deleted_message = self.customizations.messages.msg_priority_deleted
        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.delete_priority(edit_name, deleted_message)

    @pytest.mark.testrail(id=141)
    def test_add_ui_script(self):
        name = self.customizations.add.new_ui_script_name
        script = UI_SCRIPT_TEMPLATE.format(name)
        added_message = self.customizations.messages.msg_ui_script_added

        self.customizations_page.open_page(self.data.server_name + self.customizations.add_ui_script_url)
        self.customizations_page.add_ui_script(script, added_message)
        self.customizations_page.check_page(self.customizations.overview_url)
        self.customizations_page.check_ui_script(name, script, True)

        deleted_message = self.customizations.messages.msg_ui_script_deleted
        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.delete_ui_script(name, deleted_message)

    @pytest.mark.testrail(id=142)
    def test_edit_ui_script(self):
        name = self.customizations.add.new_ui_script_name
        added_message = self.customizations.messages.msg_ui_script_added
        edited_message = self.customizations.messages.msg_ui_script_edited
        edit_name = self.customizations.add.edit_ui_script_name

        script = UI_SCRIPT_TEMPLATE.format(name)
        edit_script = UI_SCRIPT_TEMPLATE.format(edit_name)

        self.customizations_page.open_page(self.data.server_name + self.customizations.add_ui_script_url)
        self.customizations_page.add_ui_script(script, added_message)
        self.customizations_page.check_page(self.customizations.overview_url)
        self.customizations_page.check_ui_script(name, script, True)

        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.edit_ui_script(name, edit_script, edited_message)
        self.customizations_page.check_page(self.customizations.overview_url)
        self.customizations_page.check_ui_script(edit_name, edit_script, False)

        deleted_message = self.customizations.messages.msg_ui_script_deleted
        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.delete_ui_script(edit_name, deleted_message)

    @pytest.mark.testrail(id=854)
    def test_edit_system_status(self):
        self.customizations_page.open_page(self.data.server_name + self.customizations.edit_system_status_passed_url)
        self.customizations_page.check_edit_status_fields()

    @pytest.mark.testrail(id=855)
    def test_add_status(self):
        # This test modifies and then restores one of the default inactive statuses
        # As it's not actually possible to create a new status by default.
        edited_message = self.customizations.messages.msg_status_edited
        data = self.customizations.status
        Status = namedtuple("Status", ["label", "name", "color_dark", "color_medium", "color_bright", "is_final", "is_active"])
        new_status = Status(data.edit_label, data.edit_name, data.edit_color_dark,
                            data.edit_color_medium, data.edit_color_bright,
                            data.edit_is_final, data.edit_is_active)

        self.customizations_page.open_page(self.data.server_name + self.customizations.edit_unnamed_status_url)
        self.customizations_page.edit_status(new_status, edited_message)
        self.customizations_page.check_page(self.customizations.overview_url)
        self.customizations_page.open_page(self.data.server_name + self.customizations.edit_unnamed_status_url)
        self.customizations_page.check_status(new_status)

        status = Status(data.label, data.name, data.color_dark, data.color_medium,
                        data.color_bright, data.is_final, data.is_active)
        self.customizations_page.open_page(self.data.server_name + self.customizations.edit_unnamed_status_url)
        self.customizations_page.edit_status(status, edited_message)
        self.customizations_page.check_page(self.customizations.overview_url)
        self.customizations_page.open_page(self.data.server_name + self.customizations.edit_unnamed_status_url)
        self.customizations_page.check_status(status)

    @pytest.mark.testrail(id=112)
    def test_delete_default_case_type(self):
        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.check_case_type_cannot_be_deleted("Other")


if __name__ == "__main__":
    pytest.main()
