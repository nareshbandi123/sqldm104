from selenium.webdriver.common.by import By


class ProjectLocator(object):
    # Overview
    overview_add_project = (By.LINK_TEXT, "Add Project")
    msg_success = (By.CSS_SELECTOR, ".message-success")
    project_single_suite = (By.LINK_TEXT, "Project - Single Suite")
    project_baseline_suite = (By.LINK_TEXT, "Project - Baseline Suite")
    project_multi_suite = (By.LINK_TEXT, "Project - Multi Suite")
    edit_first_project = (By.XPATH, "//*[@id='content-inner']/table/tbody/tr[2]/td[2]/a")
    delete_project = (By.XPATH, "td[3]/a")
    delete_dialog = (By.ID, "deleteDialog")

    # Add project
    name = (By.ID, "name")
    announcement = (By.ID, "announcement")
    show_announcement = (By.ID, "show_announcement")
    single_suite = (By.ID, "suite_mode_single")
    baseline_suite = (By.ID, "suite_mode_single_baseline")
    multi_suite = (By.ID, "suite_mode_multi")
    add_project = (By.CLASS_NAME, "button-positive")
    cancel = (By.CLASS_NAME, "button-cancel")

    # Edit project
    is_completed = (By.ID, "is_completed")
    existing_project = (By.CLASS_NAME, "hoverSensitive")

    # Access tab
    users_preview_access = (By.XPATH, "td[3]/a")

    access_options_div = (By.ID, "userAccessDropdown")