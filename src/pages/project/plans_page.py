import random
import time
from selenium.webdriver.common.by import By
from src.locators.project.plans_runs_locators import PlanRunLocators
from src.locators.general_locators import GeneralLocators
from src.pages.base_element import BasePageElement
from src.pages.base_page import BasePage
from src.pages.project.cases_page import CasesPage

class PlansPage(BasePage, BasePageElement):

    def click_add_test_plan(self):
        self.click_element(PlanRunLocators.add_plan)

    def retrieve_run_id_from_plan(self)-> int:
        parent = self.find_element_by_locator(PlanRunLocators.plan_run_container)
        try:
            element = self.find_nested_element(parent, PlanRunLocators.run_name)
        except Exception:
            # When run names have been changed, this fails to find the name
            # Which isn't an error but we can't return a run id
            return None
        value = self.get_attribute_value_from_element(element, "href")
        return self.retrieve_id_from_url(value)

    def retrieve_multiple_run_ids_from_plan(self):
        runs = self.find_elements_by_locator(PlanRunLocators.plan_run_container)
        run_links = [self.find_nested_element(run, PlanRunLocators.run_name) for run in runs]
        run_ids = []
        for link in run_links:
            value = self.get_attribute_value_from_element(link, "href")
            run_ids.append(self.retrieve_id_from_url(value))
        return run_ids

    def add_runs_to_plan(self, count:int):
        for _ in range(count):
            self.wait_for_blockui_to_close()
            self.click_element(PlanRunLocators.add_run_in_plan)

    def add_run_description(self, description:str, run_number:int=0):
        self.wait_for_blockui_to_close()
        if run_number == 0:
            self.click_element(PlanRunLocators.run_description_link)
        else:
            description_links = self.find_elements_by_locator(PlanRunLocators.run_description_link)
            description_links[run_number-1].click()
        self.send_keys_to_element(PlanRunLocators.run_edit_description, description)
        self.click_element(PlanRunLocators.run_edit_submit)

    def add_data_to_plan(self, name, description, message, add_runs=True) -> int:
        self.wait_until_not_busy()
        self.wait_for_blockui_to_close()
        self.wait_for_element_to_be_visible(GeneralLocators.name)
        self.send_keys_to_element(GeneralLocators.name, name)
        self.validate_element_text(GeneralLocators.name, name)
        self.send_keys_to_element(PlanRunLocators.run_description, description)
        if add_runs:
            self.add_runs_to_plan(random.randint(1, 5))
        self.wait_until_not_busy()
        self.wait_for_blockui_to_close()
        form = self.find_element_by_locator(GeneralLocators.form)
        self.click_nested_element(form, PlanRunLocators.add)
        self.validate_element_text(GeneralLocators.message_success, message)
        return self.retrieve_id_from_url(self.driver.current_url), self.retrieve_run_id_from_plan()

    def edit_plan(self, name, description):
        self.clear_element_data(GeneralLocators.name)
        self.clear_element_data(PlanRunLocators.run_description)
        self.send_keys_to_element(GeneralLocators.name, name)
        self.send_keys_to_element(PlanRunLocators.run_description, description)

    def add_plan_simple(self, name, description):
        self.send_keys_to_element(GeneralLocators.name, name)
        self.send_keys_to_element(PlanRunLocators.run_description, description)
        form = self.find_element_by_locator(GeneralLocators.form)
        self.wait_for_element_to_be_invisible(PlanRunLocators.block_ui)
        self.click_nested_element(form, PlanRunLocators.add)
        return self.retrieve_id_from_url(self.driver.current_url)

    def edit_plan_simple(self, name, description, message):
        self.clear_element_data(GeneralLocators.name)
        self.send_keys_to_element(GeneralLocators.name, name)
        self.clear_element_data(PlanRunLocators.run_description)
        self.send_keys_to_element(PlanRunLocators.run_description, description)
        form = self.find_element_by_locator(GeneralLocators.form)
        self.wait_for_element_to_be_invisible(PlanRunLocators.block_ui)
        self.click_nested_element(form, PlanRunLocators.add)
        self.validate_element_text(GeneralLocators.message_success, message)

    def add_assignee_to_run_in_plan(self, name:str, run_number:int=0, confirm_plan:bool=True):
        self.wait_for_blockui_to_close()
        if not run_number:
            self.click_element(PlanRunLocators.change_assignee_of_run)
        else:
            assignee_links = self.find_elements_by_locator(PlanRunLocators.change_assignee_of_run)
            assignee_links[run_number-1].click()
        dialog = self.find_element_by_locator(PlanRunLocators.run_assign_dialog)
        self.select_option_text_on_nested_element(dialog, PlanRunLocators.run_add_assignee_in_plan, name)
        self.click_nested_element(dialog, GeneralLocators.submit_button)
        self.wait_for_element_to_be_invisible(PlanRunLocators.run_assign_dialog)
        self.wait_until_not_busy()
        if confirm_plan:
            form = self.find_element_by_locator(GeneralLocators.form)
            self.click_nested_element(form, PlanRunLocators.add)

    def add_assignee_and_cases_to_run_in_plan(self, name:str, count):
        self.click_element(PlanRunLocators.change_assignee_of_run)
        dialog = self.find_element_by_locator(PlanRunLocators.run_assign_dialog)
        self.select_option_text_on_nested_element(dialog, PlanRunLocators.run_add_assignee_in_plan, name)
        self.click_nested_element(dialog, GeneralLocators.submit_button)
        self.wait_for_element_to_be_invisible(PlanRunLocators.run_assign_dialog)
        self.click_element(PlanRunLocators.run_select_cases)
        tests_to_add = self.find_elements_by_locator(PlanRunLocators.run_test_case_rows)[0:count]
        for test in tests_to_add:
            self.click_nested_element(test, GeneralLocators.checkbox)
        self.click_element(PlanRunLocators.select_case_submit)
        self.wait_for_element_to_be_invisible(PlanRunLocators.select_case_dialog)
        form = self.find_element_by_locator(GeneralLocators.form)
        self.click_nested_element(form, PlanRunLocators.add)

    def validate_run_assignee_in_plan(self, name, run_number=0):
        if not run_number:
            assignee = self.find_element_by_locator(PlanRunLocators.plan_run_assigned)
        else:
            assignees = self.find_elements_by_locator(PlanRunLocators.plan_run_assigned)
            assignee = assignees[run_number-1]
        assert name == assignee.text

    def add_assignee_and_include_all_cases_for_run_in_plan(self, name:str):
        self.click_element(PlanRunLocators.change_assignee_of_run)
        dialog = self.find_element_by_locator(PlanRunLocators.run_assign_dialog)
        self.select_option_text_on_nested_element(dialog, PlanRunLocators.run_add_assignee_in_plan, name)
        self.click_nested_element(dialog, GeneralLocators.submit_button)
        self.wait_for_element_to_be_invisible(PlanRunLocators.run_assign_dialog)
        self.click_element(PlanRunLocators.include_all_tests)
        form = self.find_element_by_locator(GeneralLocators.form)
        self.click_nested_element(form, PlanRunLocators.add)

    def select_milestone(self, milestone):
        self.select_option_text_on_element(PlanRunLocators.select_milestone, milestone)

    def validate_plan(self, name, description=None):
        # Assert the plan name is in the page
        self.find_element_by_locator(PlanRunLocators.plan_name(name))
        if description is not None:
            # Assert the plan description is in the page
            self.find_element_by_locator(PlanRunLocators.plan_description(description))

    def assert_available_plans(self, plans):
        if len(plans) == 0:
            return

        self.click_element(GeneralLocators.runs_and_results)
        plan_rows = self.find_elements_by_locator(PlanRunLocators.plan_rows)
        assert len(plan_rows) == len(plans)

        active_plans = self.find_element_by_locator(PlanRunLocators.active_plans)
        for plan in plans:
            self.find_nested_element_by_locator_and_value(active_plans, By.LINK_TEXT, plan.name)

    def add_multiple_plans(self, add_plan_url, plans, message):
        for plan in plans:
            self.open_page(add_plan_url)
            self.add_data_to_plan(plan.name, plan.description, message)
            self.validate_plan(plan.name, plan.description)

    def delete_plan(self, plan_name, message):
        self.click_element((By.LINK_TEXT, plan_name))
        self.click_element(GeneralLocators.edit_link)
        self.click_element(PlanRunLocators.delete_plan)
        self.confirm_popup_delete()
        self.validate_element_text(GeneralLocators.message_success, message)

    def delete_plans(self, message):
        while True:
            try:
                self.wait_until_not_busy()
                self.driver.implicitly_wait(2)
                plan_rows = self.find_elements_by_locator(PlanRunLocators.plan_rows)
                if len(plan_rows) == 0:
                    return

                row = plan_rows[0]
                self.click_nested_element(row, GeneralLocators.edit_link)
                self.click_element(PlanRunLocators.delete_plan)
                self.confirm_popup_delete()
                self.validate_element_text(GeneralLocators.message_success, message)
            finally:
                self.driver.implicitly_wait(10)

    def assert_plan_in_milestone(self, milestone_name, plan_name, plan_link):
        self.click_element((By.LINK_TEXT, milestone_name))
        link_element = self.find_element_by_locator((By.LINK_TEXT, plan_name))
        link = self.get_attribute_value_from_element(link_element, "href")
        assert link == plan_link

    def select_cases(self, *case_names, run_number=0, add_run=True):
        self.wait_until_not_busy()
        if add_run:
            self.click_element(PlanRunLocators.add_run_in_plan)
            # There's no busy indicator here, we have to sleep
            time.sleep(2)
        if run_number == 0:
            self.click_element(PlanRunLocators.plan_select_cases)
        else:
            select_cases_links = self.find_elements_by_locator(PlanRunLocators.plan_select_cases)
            select_cases_links[run_number-1].click()
        self.wait_for_element_to_be_visible(GeneralLocators.dialog)
        for name in case_names:
            checkbox = self.find_element_by_locator(PlanRunLocators.select_case_checkbox(name))
            if not checkbox.is_selected():
                checkbox.click()
        self.click_element(PlanRunLocators.confirm_select_cases)

    def unselect_cases(self, *case_names):
        self.wait_until_not_busy()
        self.click_element(PlanRunLocators.plan_select_cases)
        self.wait_for_element_to_be_visible(GeneralLocators.dialog)
        for name in case_names:
            checkbox = self.find_element_by_locator(PlanRunLocators.select_case_checkbox(name))
            if checkbox.is_selected():
                checkbox.click()
        self.click_element(PlanRunLocators.confirm_select_cases)
        self.wait_for_blockui_to_close()

    def assert_cases_in_run(self, *cases):
        links = self.find_elements_by_locator(PlanRunLocators.run_case_links)
        assert set(cases) == set(link.text for link in links)

    def confirm_edit_plan(self, message, popup=False):
        self.wait_until_not_busy()
        self.wait_for_blockui_to_close()
        form = self.find_element_by_locator(GeneralLocators.form)
        self.click_nested_element(form, PlanRunLocators.add)
        if popup:
            self.wait_for_element_to_be_clickable(PlanRunLocators.review_changes)
            self.click_element(PlanRunLocators.review_changes)

        self.wait_for_element_to_be_visible(GeneralLocators.message_success)
        self.validate_element_text(GeneralLocators.message_success, message)

    def rerun_plan_with_new_name(self, new_name, message):
        self.click_element(PlanRunLocators.rerun)
        form = self.find_element_by_locator(PlanRunLocators.rerun_form)
        self.click_nested_element(form, GeneralLocators.ok)
        self.clear_element_data(GeneralLocators.name)
        return self.add_data_to_plan(new_name, '', message, add_runs=False)

    def add_run_with_name(self, run_name):
        self.wait_for_blockui_to_close()
        self.click_element(PlanRunLocators.add_run_in_plan)
        self.edit_run_name(run_name)

    def edit_run_name(self, run_name, run_number=0):
        self.wait_for_blockui_to_close()
        edit_name_links = self.find_elements_by_locator(PlanRunLocators.edit_run_name_link)
        if run_number == 0:
            # edit the latest run
            edit_name_links[-1].click()
        else:
            edit_name_links[run_number-1].click()
        self.clear_element_data(PlanRunLocators.edit_run_name_textbox)
        self.send_keys_to_element(PlanRunLocators.edit_run_name_textbox, run_name)
        dialog = self.find_element_by_locator(PlanRunLocators.edit_run_name_dialog)
        self.click_nested_element(dialog, GeneralLocators.ok)

    def verify_run_names(self, run_names):
        run_blocks = self.find_elements_by_locator(PlanRunLocators.plan_run_container)
        assert len(run_blocks) == len(run_names)
        for run_block, run_name in zip(run_blocks, run_names):
            self.find_nested_element(run_block, (By.LINK_TEXT, run_name))

    def add_configuration(self, configuration_group, configuration_options):
        self.wait_for_blockui_to_close()
        self.click_element(PlanRunLocators.run_configurations)
        self.click_element(PlanRunLocators.run_configurations_add_group)
        self.send_keys_to_element(PlanRunLocators.run_configurations_group_name, configuration_group)
        self.click_element(PlanRunLocators.run_configurations_submit)
        self.wait_for_blockui_to_close()
        for option in configuration_options:
            self.click_element(PlanRunLocators.run_configurations_add_configuration)
            self.send_keys_to_element(PlanRunLocators.run_configurations_add_configuration_name, option)
            self.click_element(PlanRunLocators.run_configurations_submit)
            self.wait_for_blockui_to_close()

    def open_configurations(self):
        self.click_element(PlanRunLocators.run_configurations)

    def select_configuration_options(self, selected_options):
        self.wait_for_blockui_to_close()
        for option in selected_options:
            self.click_element(PlanRunLocators.run_configurations_option_checkbox(option))
        self.click_element(PlanRunLocators.run_configurations_select_configurations_submit)
        self.wait_until_not_busy()

    def change_configuration_options(self, all_options, selected_options):
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        for option in all_options:
            present = option in selected_options
            checkbox_locator = PlanRunLocators.run_configurations_option_checkbox(option)
            checkbox = self.find_nested_element(dialog, checkbox_locator)
            if checkbox.is_selected() != present:
                checkbox.click()

        self.click_element(PlanRunLocators.run_configurations_select_configurations_submit)

    def assert_selected_configuration_options(self, selected_options):
        options = self.find_elements_by_locator(PlanRunLocators.run_configurations_options)
        assert set(option.text for option in options) == set(selected_options)

    def assert_runs_match_configurations(self, selected_options):
        configuration_texts = set('({})'.format(option) for option in selected_options)
        runs = self.find_elements_by_locator(PlanRunLocators.test_run_title)
        assert len(runs) == len(selected_options)
        for run in runs:
            # Check the block has a run in it
            self.find_nested_element(run, PlanRunLocators.run_name)
            configuration = self.find_nested_element(run, PlanRunLocators.run_configuration_text)
            assert configuration.text in configuration_texts
            configuration_texts.remove(configuration.text)

    def assert_run_description(self, description):
        overview_container = self.find_element_by_locator(PlanRunLocators.run_overview)
        assert description in overview_container.text

    def assert_no_edit_link(self):
        self.driver.implicitly_wait(2)
        try:
            edit_links = self.find_elements_by_locator(PlanRunLocators.run_edit)
            assert len(edit_links) == 0
        finally:
            self.driver.implicitly_wait(10)

    def assert_run_closed(self, message):
        self.validate_element_text(GeneralLocators.message_help, message)

    def assert_no_close_link(self):
        tooltip_links = self.find_elements_by_locator(PlanRunLocators.run_tooltip_links)
        for tooltip in tooltip_links:
            text = tooltip.get_attribute('tooltip-header')
            assert text != 'Close Run'

    def close_plan(self):
        self.click_element(PlanRunLocators.close_plan)
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        self.click_nested_element(dialog, GeneralLocators.ok)

    def rerun_plan(self, message):
        self.click_element(PlanRunLocators.rerun)
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        self.click_nested_element(dialog, GeneralLocators.ok)
        form = self.find_element_by_locator(GeneralLocators.form)
        self.click_nested_element(form, PlanRunLocators.add)
        self.validate_element_text(GeneralLocators.message_success, message)
        return self.retrieve_id_from_url(self.driver.current_url), self.retrieve_run_id_from_plan()

    def check_error_message(self, message):
        self.validate_element_text(GeneralLocators.message_error, message)
