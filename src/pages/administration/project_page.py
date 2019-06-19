from src.locators.administration.project_locators import ProjectLocator
from src.locators.general_locators import GeneralLocators
from src.locators.project.overview_locators import OverviewLocator
from src.pages.base_element import BasePageElement
from src.pages.base_page import BasePage
from src.pages.login_page import LoginPage as login
from selenium.webdriver.common.by import By
from src.locators.dashboard_locators import DashboardLocators
from src.locators.administration.users_roles_locators import UsersRolesLocator


class ProjectPage(BasePage, BasePageElement):

    def add_single_repo_project(self, suite_name):
        self.send_keys_to_element(ProjectLocator.name, suite_name)
        self.click_element(ProjectLocator.single_suite)
        self.add()
        return self.get_project_id(suite_name)

    def add_baseline_repo_project(self, suite_name):
        self.send_keys_to_element(ProjectLocator.name, suite_name)
        self.click_element(ProjectLocator.baseline_suite)
        self.add()
        return self.get_project_id(suite_name)

    def add_multi_repo_project(self, suite_name) -> int:
        self.send_keys_to_element(ProjectLocator.name, suite_name)
        self.click_element(ProjectLocator.multi_suite)
        self.add()
        return self.get_project_id(suite_name)

    def validate(self, message, project_name):
        self.validate_element_text(ProjectLocator.msg_success, message)
        self.find_element_by_locator_and_value(By.LINK_TEXT, project_name)

    def validate_announcement_shown_in_overview(self, announcement_text):
        self.validate_element_text(OverviewLocator.announcement_area, announcement_text)

    def edit_project_name(self, project_name):
        self.clear_element_data(ProjectLocator.name)
        self.send_keys_to_element(ProjectLocator.name, project_name)
        self.click_element(ProjectLocator.add_project)

    def edit_project_announcement(self, announcement_text):
        self.clear_element_data(ProjectLocator.announcement)
        self.send_keys_to_element(ProjectLocator.announcement, announcement_text)
        self.click_element(ProjectLocator.add_project)

    def enable_showing_announcement_in_overview(self):
        self.click_element(ProjectLocator.show_announcement)
        self.click_element(ProjectLocator.add_project)

    def add(self):
        self.click_element(ProjectLocator.add_project)

    def cancel(self):
        self.click_element(ProjectLocator.cancel)

    def validate_first_project(self, message, project_name):
        self.validate_element_text(OverviewLocator.info_title, message)
        self.validate_element_text(OverviewLocator.project_link, project_name)

    def get_project_id(self, name) -> int:
        elements = self.find_elements_by_locator_and_value(By.LINK_TEXT, name)
        # get the latest element if we have projects with the same name
        value = self.get_attribute_value_from_element(elements[-1], "href")
        return self.retrieve_id_from_url(value)

    def delete_project(self, name):
        element = self.find_element_by_locator_and_value(By.LINK_TEXT, name)
        parent_row = self.find_nested_element(element, (By.XPATH, "./../.."))
        self.click_nested_element(parent_row, ProjectLocator.delete_project)
        self.confirm_delete_action()

    def confirm_delete_action(self):
        dialog = self.find_element_by_locator(ProjectLocator.delete_dialog)
        self.click_nested_element(dialog, GeneralLocators.dialog_confirm)
        self.click_nested_element(dialog, GeneralLocators.ok)

    def complete_project(self):
        self.click_element(ProjectLocator.is_completed)
        self.click_element(ProjectLocator.add_project)

    def delete_existing_projects(self):
        for p in range(self.get_existing_projects()):
            element = self.find_element_by_locator(ProjectLocator.existing_project)
            self.click_nested_element(element, ProjectLocator.delete_project)
            self.confirm_delete_action()

    def get_existing_projects(self):
        existing_projects_count = self.find_elements_by_locator(ProjectLocator.existing_project)
        return len(existing_projects_count)

    def active_completed_count_check(self, completed_projects_count, active_projects_count):
        sidebar = self.find_element_by_locator(GeneralLocators.sidebar)
        project_counts = self.find_nested_elements(sidebar, DashboardLocators.project_counts)
        active_count = self.get_attribute_value_from_element(project_counts[0], "textContent")
        completed_count = self.get_attribute_value_from_element(project_counts[1], "textContent")

        assert str(active_projects_count) == active_count
        assert str(completed_projects_count) == completed_count

    def create_projects(self, completed, active, add_project_url):
        # Creating projects
        total = active + completed
        for count in range(total):
            self.open_page(add_project_url)
            self.add_single_repo_project("TestRail Project" + "_" + str(count))

    def make_projects_completed(self, completed_project_count):
        # Completing projects
        for count in range(completed_project_count):
            self.click_element((By.LINK_TEXT, "TestRail Project" + "_" + str(count)))
            self.complete_project()

    def open_project_for_editing(self, project_name):
        element = self.find_element_by_locator_and_value(By.PARTIAL_LINK_TEXT, project_name)
        element.click()

    def open_access_tab(self):
        self.click_element(GeneralLocators.tab2)

    def change_role_for_user(self, user_id, permission):
        row = self.find_element_by_locator_and_value(By.ID, UsersRolesLocator.cn_users_row + user_id)

        self.click_nested_element(row, ProjectLocator.users_preview_access)
        self.click_element((By.LINK_TEXT, str(permission)))
        self.click_element(GeneralLocators.submit_button)
