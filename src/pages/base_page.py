import json
import pytest
from src.models.administration.user import User, Role
from src.models.administration.plugin import Plugin, UserVariable
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
import time
from typing import Any, Dict


class BasePage:

    def __init__(self, driver):
        self.driver = driver

    def open_page(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        self.wait_for_page_load(10)

    def refresh_page(self):
        self.driver.refresh()
        self.wait_for_page_load(10)

    def check_page(self, url):
        try:
            page = WebDriverWait(self.driver, 10).until(ec.url_contains(url))
        except TimeoutException:
            # id is not defined anywhere on my system so this fails
            #self.driver.get_screenshot_as_file("screenshot" + self.id() + ".png")
            self.driver.get_screenshot_as_file("screenshot-" + self.__class__.__name__ + ".png")
            raise Exception("Loading took too much time!")

    def check_page_title(self, title):
        if (self.driver.title != title):
            #self.driver.get_screenshot_as_file("screenshot" + self.id() + ".png")
            self.driver.get_screenshot_as_file("screenshot-" + self.__class__.__name__ + ".png")
            raise Exception("Expected title (" + title + ")is not displayed!")

    def wait_for_new_tab_to_open(self,seconds: int, window_count=1):
        WebDriverWait(self.driver, seconds).until(ec.number_of_windows_to_be(window_count+1))

    def open_new_tab(self, url):
        try:
            current_window_count = len(self.driver.window_handles)
            self.driver.execute_script('window.open(\''+url+'\')')
            WebDriverWait(self.driver, 10).until(ec.number_of_windows_to_be(current_window_count+1))
            self.driver.switch_to.window(self.driver.window_handles[current_window_count])
        except TimeoutException:
            raise Exception("New tab could not be opened")

    def close_tab(self):
        self.driver.close()

    def switch_to_window(self, index: int):
        self.driver.switch_to.window(self.driver.window_handles[index])

    def get_windows_count(self):
        return len(self.driver.window_handles)

    def wait_for_redirect(self, seconds):
        WebDriverWait(self.driver, seconds).until(ec.title_contains('TestRail'))
        self.wait_for_page_load(seconds)

    def check_current_url(self, uri):
        WebDriverWait(self.driver, 10).until(ec.url_contains(uri))

    def wait_for_page_load(self, seconds):
        for i in range(0, seconds*10):
            if self.driver.execute_script('return document.readyState') == 'complete':
                break
            else:
                time.sleep(0.1)