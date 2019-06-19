import time
from typing import Tuple, Any, List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.expected_conditions import NoAlertPresentException
from src.locators.general_locators import GeneralLocators
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def any_elements_displayed(elements):
    for element in elements:
        try:
            if element.is_displayed():
                return True
        except StaleElementReferenceException:
            pass
    return False


class BasePageElement(object):

    def wait_until_not_busy(self, seconds=5):
        self.driver.implicitly_wait(0)
        try:
            stop = time.time() + seconds
            while time.time() < stop:
                busy = self.find_elements_by_locator(GeneralLocators.busy)

                def is_visible(el):
                    try:
                        return el.is_displayed()
                    except StaleElementReferenceException:
                        return False

                if not any_elements_displayed(busy):
                    return
                time.sleep(0.1)
            raise Exception("Timed out waiting to not be busy")
        finally:
            self.driver.implicitly_wait(10)

    def wait_for_blockui_to_close(self, seconds=5):
        self.driver.implicitly_wait(0)
        try:
            stop = time.time() + seconds
            while time.time() < stop:
                blockUIs = self.find_elements_by_locator(GeneralLocators.blockUI)
                if not any_elements_displayed(blockUIs):
                    return
                time.sleep(0.1)
            raise TimeoutException("Timed out waiting for blockUI to go away")
        finally:
            self.driver.implicitly_wait(10)

    # Find element functions
    def find_element_by_locator(self, locator: Tuple[str, str]) -> WebElement:
        try:
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located(locator))
            element = self.driver.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            return element
        except NoSuchElementException:
            raise Exception("Element not found")

    def find_elements_by_locator(self, locator: Tuple[str, str]):
        try:
            elements = self.driver.find_elements(*locator)
            return elements
        except NoSuchElementException:
            raise Exception("Element not found")

    def find_element_by_locator_and_value(self, locator: str, value: str) -> WebElement:
        try:
            # WebDriverWait(self.driver, 10).until(ec.visibility_of_all_elements_located((locator, value)))
            element = self.driver.find_element(locator, value)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            return element
        except NoSuchElementException:
            raise Exception("Element not found")

    def find_elements_by_locator_and_value(self, locator: str, value: str) -> [WebElement]:
        try:
            elements = self.driver.find_elements(locator, value)
            return elements
        except NoSuchElementException:
            raise Exception("Element/s not found")

    def find_element_by_class_name_from_list(self, element: str, data: str) -> WebElement:
        try:
            elements = self.driver.find_elements_by_class_name(element)
            for list_item in elements:
                if list_item.get_attribute("title") == data:
                    self.driver.execute_script("return arguments[0].scrollIntoView({block: 'center'});", list_item)
                    return list_item
                else:
                    continue
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def find_nested_element(self, parent: WebElement, locator: Tuple[str, str]) -> WebElement:
        try:
            element = parent.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            return element
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def find_nested_elements(self, parent: WebElement, locator: Tuple[str, str]) -> List[WebElement]:
        return parent.find_elements(*locator)

    def find_nested_element_by_locator_and_value(self, parent: WebElement, locator: str, value: str) -> WebElement:
        try:
            element = parent.find_element(locator, value)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            return element
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    # Wait for ..
    def wait_for_element_to_be_invisible(self, locator: Tuple[str, str]):
        try:
            WebDriverWait(self.driver, 10).until(ec.invisibility_of_element_located(locator))
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def wait_for_element_to_be_visible(self, locator: Tuple[str, str]):
        try:
            WebDriverWait(self.driver, 10).until(ec.presence_of_element_located(locator))
            WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located(locator))
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def wait_for_element_to_be_clickable(self, locator: Tuple[str, str]):
        try:
            WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable(locator))
            self.wait_for_blockui_to_close()
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def wait_until_element_not_displayed(self, locator: Tuple[str, str]):
        try:
            WebDriverWait(self.driver, 10).until_not(ec.visibility_of_element_located(locator))
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    # Get value from element/attribute
    def get_attribute_value_from_element(self, web_element: WebElement, attr) -> Any:
        try:
            return web_element.get_attribute(attr)
        except NoSuchElementException:
            raise Exception("Element not found")

    # Action functions
    def click_element(self, locator: Tuple[str, str]):
        try:
            try:
                # Scroll to element and retry in case of stale element exception
                WebDriverWait(self.driver, 10, ignored_exceptions=(StaleElementReferenceException)) \
                    .until(ec.presence_of_element_located(locator))
                self.driver.execute_script("return arguments[0].scrollIntoView();", self.driver.find_element(*locator))
            except StaleElementReferenceException:
                WebDriverWait(self.driver, 10, ignored_exceptions=(StaleElementReferenceException)) \
                    .until(ec.presence_of_element_located(locator))
                self.driver.execute_script("return arguments[0].scrollIntoView();", self.driver.find_element(*locator))
            self.wait_for_element_to_be_clickable(locator)
            self.driver.find_element(*locator).click()
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def click_element_with_locator_and_value(self, locator: str, value: str):
        try:
            WebDriverWait(self.driver, 10).until(ec.visibility_of_all_elements_located((locator, value)))
            element = self.driver.find_element(locator, value)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            self.wait_for_element_to_be_clickable(locator)
            element.click()
        except NoSuchElementException:
            raise Exception("Element not found")

    def click_count_of_elements_on_list(self, locator: Tuple[str, str], count: int):
        try:
            group_users = self.driver.find_elements(*locator)
            for user in group_users:
                if (count > 0):
                    self.driver.execute_script("return arguments[0].scrollIntoView();", user)
                    user.click()
                    count = count - 1
                else:
                    continue
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def click_element_with_text_on_list(self, locator: Tuple[str, str], identifier: str):
        try:
            elements = self.driver.find_elements(*locator)
            for element in elements:
                if (element.text == identifier):
                    self.driver.execute_script("return arguments[0].scrollIntoView();", element)
                    element.click()
                else:
                    continue
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def click_nested_element(self, parent: WebElement, locator: Tuple[str, str]):
        try:
            element = parent.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            self.wait_for_blockui_to_close()
            element.click()
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def send_keys_to_element(self, locator: Tuple[str, str], value: Any):
        try:
            WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located(locator))
            self.driver.find_element(*locator).send_keys(value)
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def send_keys_to_nested_element(self, parent: WebElement, locator: Tuple[str, str], value):
        try:
            element = parent.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            element.click()
            element.send_keys(value)
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def clear_nested_element(self, parent: WebElement, locator: Tuple[str, str]):
        try:
            element = parent.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            element.clear()
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def select_option_on_element(self, locator: Tuple[str, str], value):
        try:
            element = self.driver.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            for option in element.find_elements_by_tag_name("option"):
                if option.text == value:
                    self.driver.execute_script("return arguments[0].scrollIntoView();", option)
                    option.click()
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def select_option_text_on_element(self, locator: Tuple[str, str], value: str):
        element = self.driver.find_element(*locator)
        self.driver.execute_script("return arguments[0].scrollIntoView();", element)
        select = Select(element)
        select.select_by_visible_text(value)

    def select_option_value_on_element(self, locator: Tuple[str, str], value: str):
        try:
            element = self.driver.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            select = Select(element)
            select.select_by_value(value)
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def select_option_text_on_nested_element(self, parent: WebElement, locator: Tuple[str, str], value: str):
        try:
            element = parent.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            select = Select(element)
            select.select_by_visible_text(value)
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def select_option_value_on_nested_element(self, parent: WebElement, locator: Tuple[str, str], value: str):
        try:
            element = parent.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            select = Select(element)
            select.select_by_value(value)
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def clear_element_data(self, locator: Tuple[str, str]):
        try:
            WebDriverWait(self.driver, 10).until(ec.visibility_of_all_elements_located(locator))
            element = self.driver.find_element(*locator).clear()
            return element
        except NoSuchElementException:
            raise Exception("Element not found")

    # Assert functions
    def validate_element_text(self, locator: Tuple[str, str], value: Any):
        try:
            self.wait_for_element_to_be_visible(locator)
            element = self.driver.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            text = element.text
            if text == '':
                value_attribute = element.get_attribute('value')
                if value_attribute != '':
                    text = value_attribute
            assert text == value
            return text
        except NoSuchElementException:
            raise Exception("Element not found")

    def validate_element_value(self, locator: Tuple[str, str], value: Any):
        try:
            element = self.driver.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            assert self.get_attribute_value_from_element(element, "value") == value
        except NoSuchElementException:
            raise Exception("Element not found")

    def validate_nested_element_text(self, parent: WebElement, locator: Tuple[str, str], value: str):
        try:
            WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located(locator))
            element = parent.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            assert element.text == value
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")
        except AssertionError:
            print(element.text + " vs. " + value)
            raise Exception()

    def validate_selected_option_value_on_element(self, locator: Tuple[str, str], value):
        try:
            element = self.driver.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            select = Select(element)
            assert select.first_selected_option.get_attribute("value") == value
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def validate_selected_option_text_on_element(self, locator: Tuple[str, str], value):
        try:
            WebDriverWait(self.driver, 10, ignored_exceptions=(StaleElementReferenceException)) \
                .until(ec.visibility_of_element_located(locator))
            element = self.driver.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            select = Select(element)
            print(select.first_selected_option.text + " vs. " + value)
            assert select.first_selected_option.text == value
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def retrieve_id_from_link(self, full_name) -> int:
        element = self.find_element_by_locator_and_value(By.LINK_TEXT, full_name)
        value = self.get_attribute_value_from_element(element, "href")
        return self.retrieve_id_from_url(value)

    def get_parent_element(self, element: WebElement) -> WebElement:
        try:
            return self.driver.execute_script("return arguments[0].parentNode;", element)
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def get_grandparent_element(self, element: WebElement) -> WebElement:
        try:
            return element.find_element(By.XPATH, "../../..")
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def confirm_popup_delete(self):
        self.wait_for_blockui_to_close()
        dialogs = self.find_elements_by_locator(GeneralLocators.dialog)
        for dialog in dialogs:
            if dialog.is_displayed():
                break
        else:
            raise Exception("No visible dialogs")
        self.click_nested_element(dialog, GeneralLocators.dialog_confirm)
        self.click_nested_element(dialog, GeneralLocators.ok)

    def get_link_from_link_text(self, link_text: str) -> str:
        link = self.find_element_by_locator_and_value(By.LINK_TEXT, link_text)
        return self.get_attribute_value_from_element(link, 'href')

    def retrieve_id_from_url(self, url) -> int:
        return url.split('/')[-1]

    def retrieve_id_from_string(self, string: str):
        return string.split('-')[-1]

    def check_element_is_visible(self, locator: Tuple[str, str]):
        try:
            return self.find_element_by_locator(locator).is_displayed()
        except NoSuchElementException:
            raise Exception("Element not found")
        except TimeoutException:
            raise Exception("Element not found")

    def validate_element_visibility(self, locator: Tuple[str, str]):
        try:
            element = self.driver.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            return True
        except NoSuchElementException:
            return False

    def validate_nested_element_visibility(self, parent: WebElement, locator: Tuple[str, str]):
        try:
            element = parent.find_element(*locator)
            self.driver.execute_script("return arguments[0].scrollIntoView();", element)
            return True
        except NoSuchElementException:
            return False

    def handle_alert_if_displayed(self):
        try:
            WebDriverWait(self.driver, 10).until(ec.alert_is_present())
            alert = self.driver._switch_to.alert
            alert.accept()
            WebDriverWait(self.driver, 10).until_not(ec.alert_is_present())
            self.driver.switch_to_active_element()
        except NoAlertPresentException:
            elem = self.driver.switch_to_active_element()
            elem.send_keys(Keys.ENTER)
        except TimeoutException:
            return False

    def execute_javascript(self, script):
        try:
            return self.driver.execute_script(script)
        except:
            raise Exception("Error in execution of Javascript")

    def check_element_not_exists(self, locator: Tuple[str, str]):
        try:
            self.driver.find_element(*locator)
            raise Exception("Element Found")
        except NoSuchElementException:
            return True

    def find_element_by_attribute(self, locator: Tuple[str, str], attribute, value):
        try:
            elements = self.find_elements_by_locator(locator)
            for list_item in elements:
                if list_item.get_attribute(attribute) == value:
                    self.driver.execute_script("return arguments[0].scrollIntoView();", list_item)
                    return list_item
                else:
                    continue
        except TimeoutException:
            raise Exception("Element not found")
        except NoSuchElementException:
            raise Exception("Element not found")

    def select_item_from_dropdown(self, locator: Tuple[str, str], visible_text=None, value=None, index=None):
        try:
            if visible_text:
                Select(self.find_element_by_locator(locator)).select_by_visible_text(visible_text)
            elif value:
                Select(self.find_element_by_locator(locator)).select_by_value(value)
            elif index:
                Select(self.find_element_by_locator(locator)).select_by_index(index)
            else:
                raise Exception("Invalid parameter(s) passed to select_item_from_dropdown")
        except:
            raise Exception("An Error occurred when selecting element from dropdown.")

    def hover_over_element(self, locator):
        element = self.find_element_by_locator(locator)
        hov = ActionChains(self.driver).move_to_element(element)
        hov.perform()
        hov.pause(0.2)

    def hover_over_element_and_click(self, locator):
        self.hover_over_element(locator)
        self.click_element(locator)

    def validate_success_message(self, message):
        self.wait_for_element_to_be_visible(GeneralLocators.message_success)
        self.validate_element_text(GeneralLocators.message_success, message)

    def validate_error_message(self, message):
        self.wait_for_element_to_be_visible(GeneralLocators.message_error)
        self.validate_element_text(GeneralLocators.message_error, message)

    def validate_hint_message(self, message):
        self.wait_for_element_to_be_visible(GeneralLocators.message_hint)
        self.validate_element_text(GeneralLocators.message_hint, message)

    def open_columns_dialog(self):
        self.wait_for_blockui_to_close()
        self.hover_over_element_and_click(GeneralLocators.columns_dialog)
        self.wait_until_not_busy()

    def update_columns(self):
        self.wait_for_blockui_to_close()
        self.click_element(GeneralLocators.update_columns)
        # Allow time for column change to propagate, there is no
        # reliable event to wait for.
        time.sleep(2)

    def add_column(self, column_type):
        self.open_columns_dialog()
        self.wait_until_not_busy()
        self.click_element(GeneralLocators.add_column)
        self.wait_until_not_busy()
        self.select_option_text_on_element(GeneralLocators.column_items, column_type)
        self.click_element(GeneralLocators.add_column_submit)
        self.update_columns()

    def delete_column(self, column_type):
        self.open_columns_dialog()
        self.wait_until_not_busy()
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        attempts = 0
        while True:
            try:
                attempts += 1
                row_element = self.find_nested_element(dialog, GeneralLocators.column_row_by_name(column_type))
                cells = row_element.find_elements_by_tag_name('td')
                delete = cells[5]
                WebDriverWait(self.driver, 10).until(ec.visibility_of(delete))
                delete.click()
            except (StaleElementReferenceException, ElementNotInteractableException):
                if attempts == 3:
                    raise
                continue
            break
        self.update_columns()

    def edit_column(self, column_type):
        self.wait_until_not_busy()
        self.open_columns_dialog()
        self.wait_until_not_busy()
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        row_element = self.find_nested_element(dialog, GeneralLocators.column_row_by_name(column_type))
        cells = row_element.find_elements_by_tag_name('td')
        move_up = cells[3]
        move_up.click()
        width = cells[1].find_element_by_tag_name('input')
        width.clear()
        width.send_keys('200')
        self.update_columns()

    def assert_column_exists(self, column_name):
        self.find_element_by_locator(GeneralLocators.column_header(column_name))

    def assert_column_absent(self, column_name):
        self.wait_until_not_busy()
        groups_block = self.find_element_by_locator(GeneralLocators.group_block)
        headers = self.find_nested_element(groups_block, GeneralLocators.columns_headers)
        assert column_name not in headers.text

    def assert_column_position_and_width(self, column_type, position, width):
        groups_block = self.find_element_by_locator(GeneralLocators.group_block)
        header_row = self.find_nested_element(groups_block, GeneralLocators.column_row_by_name(column_type))
        headers = header_row.find_elements_by_tag_name('th')
        column_header = headers[position]
        assert column_header.text == column_type
        assert column_header.size['width'] == width

    def set_attachment_on_input(self, input_index, filename):
        all_inputs = self.find_elements_by_locator(GeneralLocators.file_inputs)
        input_element = all_inputs[input_index]
        self.driver.execute_script(
            'arguments[0].style = ""; arguments[0].style.display = "block"; arguments[0].style.visibility = "visible";',
            input_element)
        time.sleep(0.1)
        input_element.send_keys(filename)
