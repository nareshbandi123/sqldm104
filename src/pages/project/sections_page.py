from src.locators.project.section_locators import SectionLocators
from src.locators.general_locators import GeneralLocators
from src.pages.base_element import BasePageElement
from src.pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.remote.webelement import WebElement
import time


class SectionsPage(BasePage, BasePageElement):

    def add_first_section(self, section_name:str):
        self.wait_for_element_to_be_visible(SectionLocators.addSectionInline)
        self.click_element(SectionLocators.addSectionInline)
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        self.send_keys_to_nested_element(dialog, SectionLocators.editSectionName, section_name)

    def add_subsequent_section(self, name, description=''):
        self.open_test_cases()
        self.wait_until_not_busy()
        self.add_section(name, description)
        self.wait_until_not_busy()
        self.press_add_section_button()
        self.wait_until_not_busy()

    def add_section(self, name, description=''):
        self.wait_for_blockui_to_close()
        first_section = self.find_elements_by_locator(SectionLocators.addSectionInline)
        if first_section and first_section[0].is_displayed():
            self.click_element(SectionLocators.addSectionInline)
            self.wait_until_not_busy()
            dialog = self.find_element_by_locator(GeneralLocators.dialog)
            self.send_keys_to_nested_element(dialog, SectionLocators.editSectionName, name)
            return

        self.click_element(SectionLocators.addSection)
        self.wait_until_not_busy()
        self.insert_section_data(name, description)

    def press_add_section_button(self):
        self.click_element(SectionLocators.editSectionSubmit)
        self.wait_until_not_busy()

    def hover_over_element_and_click(self, locator):
        element = self.find_element_by_locator(locator)
        hov = ActionChains(self.driver).move_to_element(element)
        hov.perform()
        self.wait_for_element_to_be_clickable(locator)
        element.click()

    def retrieve_id_from_group(self, full_name)-> int:
        group_name = self.find_element_by_locator(SectionLocators.section_title_name(full_name))
        section_id = self.get_attribute_value_from_element(group_name, "id")
        id = self.retrieve_id_from_string(section_id)
        assert (id != 0)
        return id

    def open_delete_dialog(self, id):
        section = self.find_element_by_locator_and_value(By.ID, SectionLocators.sectionName + id)
        hover = ActionChains(self.driver).move_to_element(section)
        hover.perform()
        self.click_nested_element(section, SectionLocators.sectionDelete)

    def validate_section_description(self, section_id, description):
        parent = self.find_element_by_locator_and_value(By.ID, SectionLocators.sectionColumn + section_id)
        self.validate_nested_element_text(parent, (By.ID, SectionLocators.sectionDesc + section_id), description)

    def open_test_cases(self):
        self.wait_for_element_to_be_visible(GeneralLocators.test_cases)
        self.wait_for_blockui_to_close()
        self.click_element(GeneralLocators.test_cases)
        return self.retrieve_id_from_link(GeneralLocators.title_test_cases)

    def get_suite_id(self) -> int:
        return self.retrieve_id_from_link(GeneralLocators.title_test_cases)

    def add_subsection(self, parent_id, section_name, section_description):
        parent = self.find_element_by_locator_and_value(By.ID, SectionLocators.sectionColumn + parent_id)
        self.click_nested_element(parent, SectionLocators.addSubsection)
        self.insert_section_data(section_name, section_description)

    def insert_section_data(self, section_name, section_description):
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        self.send_keys_to_nested_element(dialog, SectionLocators.editSectionName, section_name)
        self.send_keys_to_nested_element(dialog, SectionLocators.editSectionDescription, section_description)

    def get_section(self, section_name:str):
        id = self.retrieve_id_from_group(section_name)
        section = self.find_element_by_locator_and_value(By.ID, SectionLocators.sectionColumn + id)
        return section, id

    def edit_first_section_name(self, new_name):
        self.hover_over_element_and_click(SectionLocators.sectionEdit)
        self.clear_element_data(SectionLocators.editSectionName)
        self.send_keys_to_element(SectionLocators.editSectionName, new_name)
        self.click_element(SectionLocators.editSectionSubmit)
        time.sleep(1)

    def verify_new_section_name(self, name):
        self.find_element_by_locator(SectionLocators.section_title_name(name))

    def delete_section(self, name):
        section, id = self.get_section(name)
        del_link = self.find_nested_element(section, SectionLocators.sectionDelete)
        hov = ActionChains(self.driver).move_to_element(del_link)
        hov.perform()
        hov.pause(1.0)

        # refresh the elements
        section, id = self.get_section(name)
        try:
            self.click_nested_element(section, SectionLocators.sectionDelete)
        except ElementNotInteractableException:
            # happens occassionally when run as part of full test suite
            self.driver.execute_script("arguments[0].click()", del_link)
        self.confirm_popup_delete()
        self.wait_until_not_busy()

    def assert_section_count(self, num_sections):
        self.wait_until_not_busy()
        assert len(self.find_elements_by_locator(SectionLocators.sectionTitles)) == num_sections

    def add_case_to_section(self, section_name, case_name):
        self.wait_until_not_busy()
        section, id = self.get_section(section_name)
        self.click_nested_element(section, SectionLocators.addCase)
        self.wait_until_not_busy()
        self.send_keys_to_element(SectionLocators.textbox_in_section(id), case_name)
        self.click_nested_element(section, GeneralLocators.submit)
        self.wait_until_not_busy()

    def fetch_section_names(self):
        self.wait_until_not_busy()
        groups = self.find_elements_by_locator(SectionLocators.group_container)
        if len(groups) == 0:
            # If there are no sections yet the group container element doesn't exist
            return []
        titles = groups[0].find_elements(*SectionLocators.titles)
        section_names = []
        for title in titles:
            id = title.get_attribute('id')
            if not id or not id.startswith('sectionName'):
                continue
            section_names.append(title.text)
        return section_names

    def _perform_drag_and_drop_sections(self, section_1_name, section_2_name):
        section_1_id = self.retrieve_id_from_group(section_1_name)
        section_1_locator = SectionLocators.draggable_section(section_1_id)
        section_1 = self.find_element_by_locator(section_1_locator)

        section_2_id = self.retrieve_id_from_group(section_2_name)
        section_2_locator = SectionLocators.draggable_section(section_2_id)
        section_2 = self.find_element_by_locator(section_2_locator)

        chain = ActionChains(self.driver)
        chain.drag_and_drop(section_1, section_2)
        chain.perform()

    def copy_section(self, section_1_name, section_2_name):
        self._perform_drag_and_drop_sections(section_1_name, section_2_name)
        self.wait_for_element_to_be_visible(SectionLocators.drag_menu_copy)
        self.click_element(SectionLocators.drag_menu_copy)

    def move_section(self, section_1_name, section_2_name):
        self._perform_drag_and_drop_sections(section_1_name, section_2_name)
        self.wait_for_element_to_be_visible(SectionLocators.drag_menu_move)
        self.click_element(SectionLocators.drag_menu_move)

    def verify_subsection(self, section_name, subsection_name):
        section_id = self.retrieve_id_from_group(section_name)
        subsection_locator = SectionLocators.subsection_id(section_id)
        subsection = self.find_element_by_locator(subsection_locator)

        titles = subsection.find_elements(*SectionLocators.titles)
        for title in titles:
            if title.text.strip() == subsection_name:
                return
        raise AssertionError("Subsection {!r} not found in section {!r}".format(section_name, subsection_name))

    def go_to_sections(self):
        self.click_element(SectionLocators.section_link)
