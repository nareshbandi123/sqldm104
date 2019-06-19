import base64
import os
import requests
import time
from src.locators.project.results_locators import ResultsLocators
from src.locators.general_locators import GeneralLocators
from src.pages.base_element import BasePageElement
from src.pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


class ResultsPage(BasePage, BasePageElement):

    def expand_case(self, title):
        self.wait_until_not_busy()
        self.wait_for_element_to_be_visible(ResultsLocators.case_row(title))

        self.driver.implicitly_wait(4)
        try:
            add_result = self.find_elements_by_locator(ResultsLocators.add_result)
            if len(add_result) > 0 and add_result[0].is_displayed():
                # If the case view is already displayed, we just need to ensure
                # the correct row is showing.
                row = self.find_element_by_locator(ResultsLocators.case_row(title))
                if 'highlighted' in row.get_attribute('class'):
                    return

            self.hover_over_element(ResultsLocators.case_row(title))
            self.hover_over_element_and_click(ResultsLocators.expand_case_link(title))
            self.wait_until_not_busy()
            self.wait_for_element_to_be_visible(ResultsLocators.add_result)
        finally:
            self.driver.implicitly_wait(10)

    def add_result_with_comment(self, status, comment):
        self.add_result_with_status_no_confirm(status)
        self.send_keys_to_element(ResultsLocators.comment_textarea, comment)
        self.confirm_add_result()

    def add_result_with_status_no_confirm(self, status):
        self.wait_for_blockui_to_close()
        self.click_element(ResultsLocators.add_result)
        self.wait_until_not_busy()

        status_dropdown = self.find_element_by_locator(ResultsLocators.add_result_status)
        select = Select(status_dropdown)
        select.select_by_visible_text(status)

    def add_result_with_status(self, status):
        self.add_result_with_status_no_confirm(status)
        self.confirm_add_result()

    def confirm_add_result(self):
        self.wait_for_blockui_to_close()
        self.click_element(ResultsLocators.confirm_result)
        self.wait_until_not_busy()
        # The actual status isn't updated until after the busy indicator is gone
        # So we need to sleep here
        time.sleep(1)

    def assert_status(self, title, status):
        status_element = self.find_element_by_locator(ResultsLocators.case_status(title))
        print (status_element.text + " vs. " + status)
        assert status_element.text == status

    def add_result_with_dropzone_attachment(self, status, attachment_path):
        self.add_result_with_status_no_confirm(status)
        self.add_dropzone_attachment(ResultsLocators.attachment_dropzone, attachment_path)
        self.confirm_add_result()

    def add_dropzone_attachment(self, locator, attachment_path):
        filename = os.path.basename(attachment_path)
        with open(attachment_path, 'rb') as f:
            content = f.read()
        content = base64.b64encode(content).decode('ascii')

        script = (
            "var myZone, blob, base64Image; myZone = Dropzone.forElement('{}');"
            "base64content = '{}';"
            "function base64toBlob(r,e,n){{e=e||\"\",n=n||512;for(var t=atob(r),a=[],o=0;o<t.length;o+=n){{for(var l=t.slice(o,o+n),h=new Array(l.length),b=0;b<l.length;b++)h[b]=l.charCodeAt(b);var v=new Uint8Array(h);a.push(v)}}var c=new Blob(a,{{type:e}});return c}}"
            "blob = base64toBlob(base64content, 'image/png');"
            "blob.name = '{}';"
            "myZone.addFile(blob);"
        ).format(locator, content, filename)

        self.driver.execute_script(script)

    def add_result_with_image_attachment(self, status, attachment_path):
        self.add_result_with_status_no_confirm(status)
        self.click_element(ResultsLocators.add_image_link)
        self.add_dropzone_attachment(ResultsLocators.image_attachment_dropzone, attachment_path)
        self.wait_for_blockui_to_close()
        self.click_element(ResultsLocators.confirm_image_attachment)
        self.wait_until_not_busy()
        self.confirm_add_result()

    def assert_attachment_title_and_description(self, title, description):
        self.validate_element_text(ResultsLocators.attachment_title, title)
        self.validate_element_text(ResultsLocators.attachment_description, description)

    def assert_image_attachment(self, attachment_path):
        attachment = self.find_element_by_locator(('xpath', "//span[@class='markdown-img-container']/a"))
        cookies = self.driver.get_cookies()
        href = self.get_attribute_value_from_element(attachment, 'href')
        s = requests.Session()
        requests_cookies = [s.cookies.set(c['name'], c['value']) for c in cookies]
        resp = s.get(href, stream=True)
        browser_version = resp.content
        with open(attachment_path, 'rb') as f:
            original = f.read()
        assert browser_version == original

    def edit_result(self, comment):
        self.click_element(ResultsLocators.edit_result)
        self.wait_until_not_busy()
        self.clear_element_data(ResultsLocators.comment_textarea)
        self.send_keys_to_element(ResultsLocators.comment_textarea, comment)
        self.confirm_add_result()

    def assert_comment(self, comment):
        comment_element = self.find_element_by_locator(ResultsLocators.comment)
        assert comment_element.text == comment

    def assign_to(self, assign_to):
        self.select_option_text_on_element(ResultsLocators.assign_to, assign_to)

    def assert_assigned_to(self, assigned_to):
        element = self.find_element_by_locator(ResultsLocators.assigned_to)
        name_parts = assigned_to.split(' ')
        text = 'Assigned To\n{} {}.'.format(name_parts[0], name_parts[1][0])
        assert element.text == text