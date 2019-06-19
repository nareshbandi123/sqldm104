from dateutil import parser

from src.locators.administration.site_settings_locators import Sitesettings_locators
from src.locators.general_locators import GeneralLocators
from src.pages.base_element import BasePageElement
from src.pages.base_page import BasePage


class BackupsPage(BasePage, BasePageElement):
    def check_restore_button_enabled(self, is_enabled):
        self.wait_for_page_load(3)
        restore_backup_btn = self.find_element_by_locator(Sitesettings_locators.restore_backup_btn)
        assert restore_backup_btn.is_displayed()
        disabled_attr = restore_backup_btn.get_attribute("disabled")
        if disabled_attr is not None:
            button_enabled = False if disabled_attr.lower() == 'true' else True
        else:
            button_enabled = True
        assert button_enabled == is_enabled

    def restore_backup_with_confirmation(self, confirm_message, cancel=False):
        self.wait_for_page_load(3)
        self.click_element(Sitesettings_locators.restore_backup_btn)
        dialog = self.find_element_by_locator(Sitesettings_locators.restore_backup_dialog)
        self.click_nested_element(dialog, Sitesettings_locators.restore_backup_delete_checkbox)
        # type "restore backup" in input
        self.send_keys_to_nested_element(
            dialog, Sitesettings_locators.restore_backup_confirm_restore,
            confirm_message
        )
        if cancel:
            self.click_nested_element(dialog, GeneralLocators.cancel_btn)
        else:
            self.wait_for_page_load(3)
            self.click_nested_element(dialog, GeneralLocators.ok)

    def restore_backup_with_confirmation_and_cancel(self):
        self.click_element(Sitesettings_locators.restore_backup_btn)
        dialog = self.find_element_by_locator(Sitesettings_locators.restore_backup_dialog)
        self.click_nested_element(dialog, GeneralLocators.cancel_btn)

    def restore_backup_with_confirmation_ok_button_check(self):
        self.click_element(Sitesettings_locators.restore_backup_btn)
        dialog = self.find_element_by_locator(Sitesettings_locators.restore_backup_dialog)

        ok_button = self.find_nested_element(dialog, GeneralLocators.ok)
        cls = self.get_attribute_value_from_element(ok_button, 'class')
        assert "button-disabled" in cls.split()

    def check_banner_message(self, banner_message):
        self.validate_element_text(Sitesettings_locators.restore_backup_banner, banner_message)

    def cancel_restoration(self):
        try:
            # cancel restoration if needed
            self.wait_for_page_load(3)
            self.click_element(Sitesettings_locators.backup_cancel)
            return True
        except Exception as exc:
            print(exc)
            return False

    def check_banner_message_not_displayed(self):
        try:
            self.wait_for_element_to_be_invisible(Sitesettings_locators.restore_backup_banner)
            assert not self.check_element_is_visible(Sitesettings_locators.restore_backup_banner)
        except Exception:
            self.refresh_page()
            self.wait_for_element_to_be_invisible(Sitesettings_locators.restore_backup_banner)
            assert not self.check_element_is_visible(Sitesettings_locators.restore_backup_banner)

    def set_backup_time(self, param):
        self.select_option_value_on_element(Sitesettings_locators.restore_backup_hour, param)
        self.click_element(Sitesettings_locators.backup_form_save_btn)

    def get_backup_time(self):
        restore_backup_hour = self.find_element_by_locator(Sitesettings_locators.restore_backup_hour)
        return self.get_attribute_value_from_element(restore_backup_hour, "value")

    def check_backup_time(self, time):
        assert self.get_backup_time() == time

    def check_last_backup_time_is_disabled(self):
        last_backup_time = self.find_element_by_locator(Sitesettings_locators.restore_backup_last_backup_time)
        disabled = self.get_attribute_value_from_element(last_backup_time, 'disabled')
        assert disabled == 'true'

    def check_last_backup_exists(self, message):
        last_backup_time = self.find_element_by_locator(Sitesettings_locators.restore_backup_last_backup_time)
        last_backup_time_string = self.get_attribute_value_from_element(last_backup_time, 'value')
        return last_backup_time_string != message

    def check_last_backup_time_field_has_proper_date(self, message):
        last_backup_time = self.find_element_by_locator(Sitesettings_locators.restore_backup_last_backup_time)
        last_backup_time_string = self.get_attribute_value_from_element(last_backup_time, 'value')

        if last_backup_time_string != message:
            parser.parse(last_backup_time_string)

    def check_last_backup_time_field_has_message(self, message):
        last_backup_time = self.find_element_by_locator(Sitesettings_locators.restore_backup_last_backup_time)
        last_backup_time_string = self.get_attribute_value_from_element(last_backup_time, 'value')

        assert last_backup_time_string == message
