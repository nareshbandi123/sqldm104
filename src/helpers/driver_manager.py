from selenium import webdriver
from enum import Flag

class DriverType(Flag):
    FIREFOX = 1
    CHROME = 2
    IE = 3
    EDGE = 4
    PHANTOMJS = 5
    SAFARI = 6
    OPERA = 7
    REMOTE = 8

    @staticmethod
    def get_driver_type(browserName: str):
        driverNames ={
            "firefox":    DriverType.FIREFOX,
            "chrome":     DriverType.CHROME,
            "ie":         DriverType.IE,
            "edge":       DriverType.EDGE,
            "phantomjs":  DriverType.PHANTOMJS,
            "safari":     DriverType.SAFARI,
            "opera":      DriverType.OPERA,
            "remote":     DriverType.REMOTE
        }
        browser = driverNames[browserName.lower()]
        if browser is None:
            raise ValueError("Browser not found: " + browserName)

        return browser


class DriverOptions():
    attrs = {}
    meths = {}

class DriverManager:

    def __init__(self, driver:webdriver):
        self.driver = driver

    # options parameter needs to contist of:
    #  - options.attrs for attributes to set like headless
    #  - options.meths for methods to call (no parameters supported yet)
    @staticmethod
    def get_driver(browserName: DriverType, options: DriverOptions = None, capabilities = None, commandExecutor = None):
        driver = DriverManager._get_driver_object(browserName, capabilities, commandExecutor)
        if driver is None:
            raise NotImplementedError(str(browserName) + " not supported right now!")

        DriverManager._set_web_driver_options(driver, options)

        return driver

    @staticmethod
    def start_service(driver, serverName: str):
        DriverManager._check_if_driver_exists(driver)
        driver.maximize_window()
        driver.get(serverName)
        driver.implicitly_wait(10)

    @staticmethod
    def quit_driver(driver):
        driver.delete_all_cookies()
        driver.quit()

    @staticmethod
    def _check_if_driver_exists(driver):
        if driver is None:
            raise RuntimeError("Webdriver is \'None\'")

    @staticmethod
    def _set_web_driver_options(driver, options: DriverOptions):
        if hasattr(driver, 'options'):
            for key, value in options.attrs.items():
                setattr(driver.options, key, value)


        def func_not_found(func_name):
            print("No function " + func_name + " found!")

        for key in options.meths.items():
            func = getattr(driver, str(key), func_not_found(key))
            func()

    @staticmethod
    def _get_driver_object(browserName, capabilities, executor):
        drivers = {
            DriverType.FIREFOX:  webdriver.Firefox,
            DriverType.CHROME:  webdriver.Chrome,
            DriverType.IE:  webdriver.Ie,
            DriverType.EDGE:  webdriver.Edge,
            DriverType.PHANTOMJS:  webdriver.PhantomJS,
            DriverType.SAFARI:  webdriver.Safari,
            DriverType.OPERA:  webdriver.Opera,
            DriverType.REMOTE:  webdriver.Remote
        }
        driver = drivers.get(browserName)

        if browserName is DriverType.REMOTE:
            return driver(command_executor=executor,
                        desired_capabilities=capabilities)

        return driver(desired_capabilities=capabilities)
