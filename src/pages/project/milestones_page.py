from datetime import date
from selenium.webdriver.common.by import By
from src.locators.general_locators import GeneralLocators
from src.locators.project.milestones_locators import MilestonesLocators
from src.pages.base_element import BasePageElement
from src.pages.base_page import BasePage


class MilestonesPage(BasePage, BasePageElement):

    def add_milestone(self, name, description):
        self.send_keys_to_element(GeneralLocators.name, name)
        self.send_keys_to_element(GeneralLocators.description, description)

    def confirm_milestone(self, message):
        self.click_element(MilestonesLocators.add_milestone)
        self.validate_element_text(GeneralLocators.message_success, message)

    def validate_milestone(self, name, description):
        self.click_element((By.LINK_TEXT, name))

        # Assert the milestone name is in the page
        self.find_element_by_locator(MilestonesLocators.milestone_name(name))

        # Assert the milestone description is in the page
        self.find_element_by_locator(MilestonesLocators.milestone_description(description))

    def get_milestone_link(self, name):
        element = self.find_element_by_locator_and_value(By.LINK_TEXT, name)
        value = self.get_attribute_value_from_element(element, "href")
        return value

    def get_milestone_links(self, names):
        results = []
        for name in names:
            results.append(self.get_milestone_link(name))
        return results

    def verify_milestone_link_exists(self, name, link):
        element = self.find_element_by_locator_and_value(By.LINK_TEXT, name)
        value = self.get_attribute_value_from_element(element, "href")
        assert value == link

    def verify_milestone_links_exist(self, names, links):
        for name, link in zip(names, links):
            self.verify_milestone_link_exists(name, link)

    def select_start_date(self):
        self.click_element(MilestonesLocators.start_date)
        today = date.today()
        self.wait_for_element_to_be_visible(MilestonesLocators.date_picker)
        calendar = self.find_element_by_locator(MilestonesLocators.date_picker)
        # Click on today
        self.click_nested_element(calendar, (By.LINK_TEXT, str(today.day)))
        today_string = '{}/{}/{}'.format(today.month, today.day, today.year)
        self.validate_element_text(MilestonesLocators.start_date, today_string)
        return today_string

    def select_end_date(self):
        self.click_element(MilestonesLocators.end_date)
        # Pick the first day of the next month
        self.click_element(MilestonesLocators.next_month)
        date_picker = self.find_element_by_locator(MilestonesLocators.date_picker)
        self.click_nested_element(date_picker, MilestonesLocators.first_day)

        def get_start_date_of_next_month():
            today = date.today()
            day = 1
            month = today.month + 1 if today.month < 12 else 1
            year = today.year if today.month < 12 else today.year + 1
            due_date_string = '{}/{}/{}'.format(month, day, year)
            return due_date_string

        due_date = get_start_date_of_next_month()
        self.validate_element_text(MilestonesLocators.end_date, due_date)
        return due_date

    def confirm_start_date(self, name, start_date):
        milestone_id = self.retrieve_id_from_link(name)
        start_date_locator = MilestonesLocators.milestone_start_date(milestone_id, start_date)
        # If this query succeeds then the start date has been set correctly
        self.find_element_by_locator(start_date_locator)

    def confirm_due_date(self, name, due_date):
        self.click_element((By.LINK_TEXT, name))
        self.find_element_by_locator(MilestonesLocators.milestone_due_date(due_date))

    def delete_milestone(self, name, message):
        self.click_element((By.LINK_TEXT, name))
        self.click_element(MilestonesLocators.edit)
        self.click_element(MilestonesLocators.delete)
        self.confirm_popup_delete()
        self.validate_element_text(GeneralLocators.message_success, message)

    def verify_milestone_has_active_run(self, name):
        milestone_id = self.retrieve_id_from_link(name)
        milestone_locator = (By.ID, "milestone-{}".format(milestone_id))
        milestone_div = self.find_element_by_locator(milestone_locator)

        # If the run is linked to the milestone, this lookup will succeed
        milestone_div.find_element(*MilestonesLocators.has_active_run)

    def add_multiple_milestones(self, milestones, add_url, overview_url, message):
        for milestone in milestones:
            self.open_page(add_url)
            self.add_milestone(milestone.name, milestone.description)
            self.confirm_milestone(message)
            self.check_page(overview_url)
            self.validate_milestone(milestone.name, milestone.description)
