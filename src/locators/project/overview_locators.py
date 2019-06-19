from selenium.webdriver.common.by import By


class OverviewLocator(object):

    info_title = (By.CLASS_NAME, "empty-title")
    project_link = (By.CLASS_NAME, "link-noline")
    announcement_area = (By.CLASS_NAME, "markdown")