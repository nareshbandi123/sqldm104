from selenium.webdriver.common.by import By


class DashboardLocators(object):
    # user section
    username = (By.CLASS_NAME, 'dropdownLink')
    administration = (By.LINK_TEXT, 'Administration')
    logout = (By.LINK_TEXT, 'Logout')
    my_settings = (By.LINK_TEXT, 'My Settings')

    # Dashboard
    dashboard_tab = (By.LINK_TEXT, "Dashboard")

    # Side tab
    add_project = (By.CLASS_NAME, "sidebar-button")
    project_counts = (By.CLASS_NAME, "text-softer")

