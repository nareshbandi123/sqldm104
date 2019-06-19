from selenium.webdriver.common.by import By


class ReportsLocator(object):
    schedule_on_demand_via_api = (By.ID, "schedule_on_demand_via_api")
    button_add_report = (By.ID, "submit")
    table_grid = (By.CSS_SELECTOR, "table.grid")
    delete_report = (By.XPATH, "td[7]/a")
    delete_dialog = (By.ID, "deleteDialog")

    report_name = (By.ID, "name")
    report_description = (By.ID, "description")
