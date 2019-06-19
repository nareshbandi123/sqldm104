from selenium.webdriver.common.by import By


class MilestonesLocators(object):

    add_milestone = (By.XPATH, "//button[@type='submit' and contains(., 'Add Milestone')]")

    start_date = (By.ID, "start_on")
    end_date = (By.ID, "due_on")

    edit = (By.LINK_TEXT, 'Edit')
    delete = (By.LINK_TEXT, "Delete this milestone")

    # Calendar elements
    date_picker = (By.ID, "ui-datepicker-div")
    highlighted_day = (By.CSS_SELECTOR, "a.ui-state-highlight")
    next_month = (By.CSS_SELECTOR, "a.ui-datepicker-next")
    first_day = (By.XPATH, "//a[contains(., '1')]")

    has_active_run = (By.XPATH, "//div[contains(., 'Has 1 active test run.')]")

    @classmethod
    def milestone_name(cls, name):
        return (By.XPATH, "//div[contains(.,'{}')]".format(name))

    @classmethod
    def milestone_description(cls, description):
        return (By.XPATH, "//p[contains(.,'{}')]".format(description))

    @classmethod
    def milestone_start_date(cls, id, start_date):
        milestone_id = "milestone-{}".format(id)
        return (By.XPATH, "//div[@id='{}' and contains(., 'Starts on {}')]".format(milestone_id, start_date))

    @classmethod
    def milestone_due_date(cls, due_date):
        due_date_xpath = "//div[@class='sidebar-inner' and contains(., 'Due on {}.')]".format(due_date)
        return (By.XPATH, due_date_xpath)
