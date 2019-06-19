from selenium.webdriver.common.by import By


class LoginLocators(object):
    # Login
    email_address = (By.ID, 'name')
    password = (By.ID, 'password')
    remember_me = (By.ID, 'rememberme')
    login = (By.ID, 'button_primary')
    forgot_password = (By.CLASS_NAME, 'loginpage-forgotpassword')
    version = (By.CLASS_NAME, 'button-info')
    message_success = (By.CLASS_NAME, "message-success")
    error_message = (By.CLASS_NAME, "message-error")
    sso_login = (By.ID, "button_sso")
    error_email = (By.CLASS_NAME, "loginpage-message ")
    login_error_text = (By.CLASS_NAME, "error-text")

    #SSO IDP (Okta) Locators
    sso_username = (By.ID, "okta-signin-username")
    sso_password = (By.ID, "okta-signin-password")
    sso_signin = (By.ID, "okta-signin-submit")
    okta_sign_in_failed = (By.CLASS_NAME, "infobox-error")
    okta_usericon = (By.CLASS_NAME, "option-selected-text")
    okta_usermenu = (By.CLASS_NAME, "option-title")

    # Forgot Password
    fp_email_address = (By.CLASS_NAME, "login-input ")
    request_password_reset = (By.CLASS_NAME, "forgot_passwordpage-request-login")
    cancel = (By.CLASS_NAME, "forgot_passwordpage-request-cancel")
    fp_error_message = (By.CLASS_NAME, "loginpage-message ")
    fp_message = (By.CLASS_NAME, "error-text")
