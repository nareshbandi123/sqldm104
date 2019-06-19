from src.locators.project.plans_runs_locators import PlanRunLocators
from src.locators.general_locators import GeneralLocators
from src.pages.base_element import BasePageElement
from src.pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


class RunsPage(BasePage, BasePageElement):

    def add_run_with_case_in_section(self, section_name, run_name):
        self.click_add_test_run()
        self.select_cases_from_section(section_name)
        return self.add_data_to_run(run_name)

    def click_add_test_run(self):
        self.click_element(PlanRunLocators.add_run)

    def confirm_suite(self):
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        self.click_nested_element(dialog, GeneralLocators.ok)

    def add_data_to_run(self, name, description=None) -> int:
        self.clear_element_data(GeneralLocators.name)
        self.send_keys_to_element(GeneralLocators.name, name)
        if description is not None:
            self.send_keys_to_element(PlanRunLocators.run_description, description)
        form = self.find_element_by_locator(GeneralLocators.form)
        self.wait_for_blockui_to_close()
        self.click_nested_element(form, GeneralLocators.add)
        return self.retrieve_id_from_url(self.driver.current_url)

    def select_cases_from_section(self, section_name):
        self.click_element(PlanRunLocators.include_specific_cases)
        self.click_element(PlanRunLocators.run_select_cases)
        self.click_element(PlanRunLocators.select_cases_by_section_name(section_name))
        self.click_element(PlanRunLocators.select_case_submit)

    def add_data_to_run_with_milestone(self, name, description, milestone):
        milestone_element = self.find_element_by_locator(PlanRunLocators.select_milestone)
        selector = Select(milestone_element)
        selector.select_by_visible_text(milestone)
        return self.add_data_to_run(name, description)

    def delete_run(self):
        self.click_element(PlanRunLocators.delete_run)
        self.confirm_popup_delete()

    def edit_assignee_and_save_run(self, assigned_to):
        if assigned_to:
            self.select_option_on_element(PlanRunLocators.assigned_to, assigned_to)
        form = self.find_element_by_locator(GeneralLocators.form)
        self.click_nested_element(form, GeneralLocators.add)

    def assign_to(self, assigned_to):
        self.select_option_on_element(PlanRunLocators.assigned_to, assigned_to)

    def validate_run_assignee(self, assigned_to:str):
        type_box = self.find_element_by_locator(PlanRunLocators.assigned_to)
        select = Select(type_box)
        selected_field_type = select.first_selected_option.text
        assert selected_field_type == assigned_to

    def close_run(self):
        self.click_element(PlanRunLocators.close_run)
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        self.click_nested_element(dialog, GeneralLocators.ok)
        self.wait_for_element_to_be_invisible(GeneralLocators.dialog)

    def verify_run(self, name, description):
        overview_container = self.find_element_by_locator(PlanRunLocators.run_overview)
        assert description in overview_container.text
        self.validate_element_text(PlanRunLocators.run_title, name)

    def verify_run_link(self, name):
        self.find_elements_by_locator((By.LINK_TEXT, name))

    def all_run_ids(self):
        runs = self.find_elements_by_locator(PlanRunLocators.edit_run_name_link)
        return [self.retrieve_id_from_url(run.get_property('href')) for run in runs]

    def select_milestone(self, milestone):
        self.select_option_text_on_element(PlanRunLocators.select_milestone, milestone)

    def assert_run_in_milestone(self, milestone_name, run_name, run_link):
        self.click_element((By.LINK_TEXT, milestone_name))
        link_element = self.find_element_by_locator((By.LINK_TEXT, run_name))
        link = self.get_attribute_value_from_element(link_element, "href")
        assert link == run_link

    def assert_cases_in_run(self, cases):
        links = self.find_elements_by_locator(PlanRunLocators.run_case_links)
        assert set(cases) == set(link.text for link in links)

    def select_cases(self, *case_names):
        self.wait_until_not_busy()
        self.click_element(PlanRunLocators.include_specific_cases)
        self.click_element(PlanRunLocators.run_select_cases)
        self.wait_for_element_to_be_visible(GeneralLocators.dialog)
        for name in case_names:
            checkbox = self.find_element_by_locator(PlanRunLocators.select_case_checkbox(name))
            if not checkbox.is_selected():
                checkbox.click()
        self.click_element(PlanRunLocators.confirm_select_cases)

    def edit_run(self, run):
        self.clear_element_data(GeneralLocators.name)
        self.clear_element_data(PlanRunLocators.run_description)
        self.send_keys_to_element(GeneralLocators.name, run.name)
        self.send_keys_to_element(PlanRunLocators.run_description, run.description)
        self.select_option_on_element(PlanRunLocators.assigned_to, run.assigned_to)
        milestone_element = self.find_element_by_locator(PlanRunLocators.select_milestone)
        selector = Select(milestone_element)
        selector.select_by_visible_text(run.milestone)

    def confirm_edit_run(self, message):
        form = self.find_element_by_locator(GeneralLocators.form)
        self.click_nested_element(form, GeneralLocators.ok)
        self.validate_success_message(message)

    def rerun_run(self, message, statuses=None):
        self.wait_for_blockui_to_close()
        self.click_element(PlanRunLocators.rerun)
        self.wait_until_not_busy()
        if statuses is not None:
            statuses_element = self.find_element_by_locator(PlanRunLocators.rerun_statuses)
            labels = statuses_element.find_elements_by_tag_name('label')
            inputs = statuses_element.find_elements_by_tag_name('input')
            for label, input in zip(labels, inputs):
                # by default all statuses are selected, so if we're not selecting a status
                # we need to click the checkbox.
                if label.text not in statuses:
                    input.click()

        dialog = self.find_element_by_locator(PlanRunLocators.rerun_form)
        self.click_nested_element(dialog, GeneralLocators.ok)
        self.wait_until_not_busy()
        form = self.find_element_by_locator(GeneralLocators.form)
        self.click_nested_element(form, PlanRunLocators.add)
        self.validate_element_text(GeneralLocators.message_success, message)

    def assert_no_edit_link(self):
        self.driver.implicitly_wait(2)
        try:
            edit_links = self.find_elements_by_locator(PlanRunLocators.run_edit)
            assert len(edit_links) == 0
        finally:
            self.driver.implicitly_wait(10)

    def assert_run_deleted(self, run_id):
        all_ids = self.all_run_ids()
        assert run_id not in all_ids