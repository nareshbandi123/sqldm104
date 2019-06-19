from selenium.webdriver.common.by import By


class AdministrationLocators(object):

    overview = (By.LINK_TEXT, "Overview")
    projects = (By.LINK_TEXT, "Projects")
    view_projects = (By.LINK_TEXT, "View projects")
    add_project = (By.LINK_TEXT, "Add a new project")
    users_roles = (By.LINK_TEXT, "Users & Roles")
    forget_user = (By.LINK_TEXT, "Forget this user")

    banner = (By.CLASS_NAME, "empty-with-explanation")
    banner_title = (By.CLASS_NAME, "empty-title")
    banner_body = (By.CLASS_NAME, "empty-body")


