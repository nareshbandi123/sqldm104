from selenium.webdriver.common.by import By


class CaseLocators(object):

    case_assigned = (By.CLASS_NAME, "assigned")
    case_assign_dialog = (By.ID, "addCommentDialog")
    case_assign_select = (By.ID, "addCommentAssignTo")
    case_assign_submit = (By.ID, "addCommentSubmit")
