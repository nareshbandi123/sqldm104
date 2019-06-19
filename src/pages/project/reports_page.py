from selenium.webdriver.common.by import By

from src.helpers.api_client import APIError
from src.locators.administration.project_locators import ProjectLocator
from src.locators.general_locators import GeneralLocators
from src.locators.project.reports_locators import ReportsLocator
from src.pages.base_element import BasePageElement
from src.pages.base_page import BasePage


class ReportsPage(BasePage, BasePageElement):

    def check_schedule_on_demand_via_api(self):
        self.click_element(ReportsLocator.schedule_on_demand_via_api)

    def click_add_report(self):
        self.click_element(ReportsLocator.button_add_report)

    def check_api_template_appears_on_the_page(self, template_title):
        return self.find_element_by_locator((By.LINK_TEXT, template_title))

    def edit_report_template_by_title(self, template_title):
        link = self.check_api_template_appears_on_the_page(template_title)
        link.click()

    def check_api_on_demand_checkbox_disabled_and_selected(self):
        element = self.find_element_by_locator(ReportsLocator.schedule_on_demand_via_api)

        assert element.is_selected()
        assert not element.is_enabled()

    def change_name(self, new_name):
        self.clear_element_data(ReportsLocator.report_name)
        self.send_keys_to_element(ReportsLocator.report_name, new_name)
        self.click_add_report()

    def delete_report(self, name):
        element = self.find_element_by_locator_and_value(By.LINK_TEXT, name)
        parent_row = self.find_nested_element(element, (By.XPATH, "./../.."))
        self.click_nested_element(parent_row, ReportsLocator.delete_report)
        self.confirm_delete_action()

    def verify_deletion_of_report(self, report_name):
        return self.check_element_not_exists((By.LINK_TEXT, report_name))

    def confirm_delete_action(self):
        dialog = self.find_element_by_locator(ReportsLocator.delete_dialog)
        self.click_nested_element(dialog, GeneralLocators.ok)

    def check_reports_length(self, reports, count):
        assert len(reports) == count

    def expect_report_contents_check(self, report):
        del report['id']
        expected_report = {
            'name': 'Property Distribution New Name',
            'description': None,
            'notify_user': False,
            'notify_link': False,
            'notify_link_recipients': None,
            'notify_attachment': False,
            'notify_attachment_recipients': 'person1@example.com\r\nperson2@example.com',
            'notify_attachment_html_format': False,
            'notify_attachment_pdf_format': False,
            'cases_groupby': 'cases:priority_id',
            'suites_include': '1',
            'suites_ids': None,
            'sections_include': '1',
            'sections_ids': None,
            'cases_columns': {
                'cases:id': 75,
                'cases:title': 0
            },
            'cases_filters': None,
            'cases_limit': 25,
            'content_hide_links': False,
            'cases_include_summary': True,
            'cases_include_details': True
        }
        assert report == expected_report

    def check_report_links_in_response(self, resp):
        assert resp['report_url']
        assert resp['report_html']
        assert resp['report_pdf']

    def check_status_code_and_error(self, exc: APIError, expected_code, expected_error, alt_error=None):
        assert exc.status_code == expected_code
        if alt_error:
            assert exc.error_text.startswith(expected_error) or exc.error_text.startswith(alt_error)
        else:
            assert exc.error_text.startswith(expected_error)

    def expect_to_raise_exception(self, callback, args, code, error, alt_error=None):
        try:
            callback(*args)
            assert False
        except APIError as exc:
            self.check_status_code_and_error(exc, code, error, alt_error)

    def validate_success_message(self, message):
        self.validate_element_text(ProjectLocator.msg_success, message)
