from src.pages.base_page import BasePage
from src.pages.base_element import BasePageElement
from src.locators.dashboard_locators import DashboardLocators


class DashboardPage(BasePage, BasePageElement):

    def open_administration(self):
        self.click_element(*DashboardLocators.administration)