from src.pages.base_page import BasePage
from src.pages.base_element import BasePageElement
from src.locators.administration.administration_locators import AdministrationLocators
from selenium.webdriver.common.by import By


class AdministrationPage(BasePage, BasePageElement):

    def click_projects(self):
        self.click_element(*AdministrationLocators.projects)

    def click_new_project(self):
        self.click_element(*AdministrationLocators.add_project)

    def check_banner_text(self, banner_header, banner_body):
        assert str.rstrip(str.lstrip(self.find_element_by_locator(AdministrationLocators.banner_title).text)) == banner_header
        assert str.rstrip(str.lstrip(self.find_element_by_locator(AdministrationLocators.banner_body).find_element_by_tag_name('p').text)) == banner_body

    def check_link(self, link_text, link):
        self.click_element((By.LINK_TEXT, link_text))
        self.wait_for_page_load(10)
        assert link in self.driver.current_url
        self.driver.back()

