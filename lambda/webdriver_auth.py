import json
import logging
import os
import time
from typing import Tuple

import requests
from requests.cookies import RequestsCookieJar
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


logger = logging.getLogger()


def first(items, func):
    for item in items:
        if func(item):
            return item
    return None


def any(items, func):
    for item in items:
        if func(item):
            return True
    return False


def foreach(items, func):
    for item in items:
        func(item)


def empty(items):
    if items is not None and len(items) > 0:
        return True
    return False


wire_logger = logging.getLogger(
    'seleniumwire.handler').setLevel(level=logging.WARNING)


class SeleniumAuthConstants:
    LOGIN_URL = 'https://www.myfitnesspal.com/account/login'
    LOGGER_NAME = 'seleniumauth'
    TERMINAL_REQUEST = 'featured_blog_posts'


class Element:
    EMAIL_NAME = 'email'
    PASSWORD_NAME = 'password'
    ACCEPT_COOKIES_XPATH = "//button[@title='ACCEPT']"
    COOKIE_IFRAME_XPATH="//iframe[@title='SP Consent Message']"
    SUBMIT_XPATH = "//button[@type='submit']"
    TOOLBAR_XPATH = "//span[contains(@class,'MuiContainer-maxWidthLg')]"


class SeleniumAuth:
    @property
    def cookies(
        self
    ):
        '''
        The raw cookie data returned from the
        webdriver requests or stored credentials
        '''

        return self.__cookies

    @property
    def cookiejar(
        self
    ) -> RequestsCookieJar:
        '''
        A `RequestsCookieJar` with the cookies captured 
        from the webddriver or from loaded credentials.  
        '''

        return self.__cookiejar

    def __init__(
        self,
        username: str,
        password: str,
        webdriver_path: str,
        creds_filepath: str = None,
        use_stored_credentials: bool = True
    ):
        self.__username = username
        self.__password = password
        self.__webdriver_path = webdriver_path
        self.__creds_filepath = creds_filepath
        self.__use_stored_credentials = use_stored_credentials

        self.__driver: webdriver.Chrome = None

        self.__cookies = list()
        self.__cookiejar = None

    def __initialize_driver(self) -> webdriver.Chrome:
        ''' Create and configure the Chrome webdriver '''

        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("--start-maximized")
        options.add_argument("--kiosk")

        driver = webdriver.Chrome(
            self.__webdriver_path,
            options=options)

        '''driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install())  ,
            options=options
        )'''

        driver.set_window_size(1920, 1080)
        driver.maximize_window()

        driver.set_page_load_timeout(60)

        print('driver initialized')
        self.__driver = driver

    def __navigate(
        self
    ) -> None:
        '''
        Navigate to service login page
        '''

        self.__driver.get(
            url=SeleniumAuthConstants.LOGIN_URL)

    def __get_login_input_elements(
        self
    ) -> Tuple[WebElement, WebElement]:
        ''' Get the login username and password elements '''

        print('Waiting for email element')
        email = self.__get_element(
            _type='name',
            selector=Element.EMAIL_NAME)

        print(f'Waiting for password element')
        password = self.__get_element(
            _type='name',
            selector=Element.PASSWORD_NAME)

        return email, password

    def __create_cookiejar(
        self,
        cookies=None
    ) -> Tuple[RequestsCookieJar, dict]:
        '''
        Create a cookiejar from the captured driver cookies and
        return the created cookie jar and the source dictionary

        '''

        raw_cookies = cookies or self.__driver.get_cookies()

        if self.__driver:
            self.__driver.quit()

        if not empty(raw_cookies or []):
            raise Exception('Failed to capture driver cookies')

        # Convert the dictionary of cookie values returned from
        # the driver or loaded from stored credentials into a
        # requests cookiejar (derived from http.CookieJar used
        # by MFP client)
        print(f'Creating requests session cookiejar')
        session = requests.session()

        foreach(raw_cookies, lambda cookie: session.cookies.set(
            name=cookie.get('name'),
            value=cookie.get('value'))
        )

        print('setting auth cookie jar')
        self.__cookiejar = session.cookies
        #print(self.__cookiejar)
        self.__cookies = raw_cookies

        if (self.__use_stored_credentials
                and self.__creds_filepath is not None):
            print('saving cookies')
            self.__save_credentials()
        else:
            print('cookie saving disabled')

    def __get_element(
        self,
        _type: str,
        selector: str,
        max_wait_time=30
    ) -> WebElement:
        '''
        Explicitly wait for an element to become available
        on the page and return the element

        `type`: element type
        `value`: element path
        `max_wait_time`: maximum time to wait before timeout
        '''

        locator = (_type, selector)

        element = WebDriverWait(
            driver=self.__driver,
            timeout=max_wait_time).until(
                method=EC.presence_of_element_located((
                    locator)))

        return element

    def __get_submit(
        self
    ) -> WebElement:
        ''' Get the login page submit button element '''

        print(f'Locating submit element')
        submit = self.__get_element(
            _type='xpath',
            selector=Element.SUBMIT_XPATH)

        if isinstance(submit, list):
            return submit[0]

        return submit

    def __get_accept(
        self
    ) -> WebElement:
        ''' Get the login page submit button element '''

        print(f'Locating accept element')
        accept = self.__get_element(
            _type='xpath',
            selector=Element.ACCEPT_COOKIES_XPATH)

        print(f'Accept element: {accept}')

        if isinstance(accept, list):
            return accept[0]

        return accept

    def __get_cookie_iframe(
        self
    ) -> WebElement:
        ''' Get the login page submit button element '''

        print(f'Locating cookie iframe element')
        iframe = self.__get_element(
            _type='xpath',
            selector=Element.COOKIE_IFRAME_XPATH)

        print(f'Iframe element: {iframe}')

        if isinstance(iframe, list):
            return iframe[0]

        return iframe



    def __get_distinct_request_urls(
        self
    ):
        '''
        Get a list of all distinct request URLs from
        the webdriver
        '''

        urls = set([
            req.url for req in self.__driver.requests
        ])

        return list(urls)

    def __wait_for_login(
        self,
        max_wait_time: int
    ) -> None:
        '''
        Wait for the login to complete indicated by
        the toolbar element becoming available on the
        page before exiting.  Otherwise seleniumwire
        may not capture the full network trace for the
        login and the required cookies

        `max_wait_time` : maximum time to wait on the
        toolbar element, this may
        '''

        # Use the XHR request that fetches the spash page's blog
        # post list as an idicator that we've captured all the
        # auth-related requests.  Otherwise the driver may exit
        # before this happens

        def terminal_request_receieved(driver: webdriver.Chrome):
            distinct_urls = self.__get_distinct_request_urls()

            if any(items=distinct_urls,
                   func=lambda url: SeleniumAuthConstants.TERMINAL_REQUEST in url):
                print(f'Terminal request received')
                return True

        WebDriverWait(
            driver=self.__driver,
            timeout=max_wait_time).until(
                method=terminal_request_receieved)

        print(f'Terminal login request receieved')

    def __login(
        self,
        max_wait_time: int
    ) -> RequestsCookieJar:
        '''
        Internal login routine, to be wrapped in try/except
        to capture and return specific exceptions concerning
        timeouts
        '''

        # Attempt to load stored credentials and use those if
        # available
        if (self.__use_stored_credentials
                and os.path.exists(self.__creds_filepath)):

            print('Using stored credentials')
            return self.load_credentials()

        print('No stored credentials found, using webdriver')

        self.__initialize_driver()
        self.__navigate()

        cookie_iframe = self.__get_cookie_iframe()

        #switch to the iframe
        self.__driver.switch_to.frame(cookie_iframe)

        print('switched to iframe')

        #click the accept button
        accept = self.__get_accept()
        accept.click()

        #switch back 
        self.__driver.switch_to.default_content()
        print('switched to default content')

        #login to myfitness pal
        usr, pwd = self.__get_login_input_elements()

        usr.send_keys(self.__username)
        pwd.send_keys(self.__password)

        submit = self.__get_submit()
        submit.click()

        #self.__wait_for_login(
        #    max_wait_time=max_wait_time)
        print('logging in')
        time.sleep(15)

        print('creating cookiejar...')
        self.__create_cookiejar()

    def __save_credentials(
            self
    ) -> None:
        '''
        Export and save a JSON file containing the raw
        cookie data
        '''

        with open(self.__creds_filepath, 'w') as file:
            file.write(json.dumps(self.__cookies))

    def load_credentials(
        self
    ) -> bool:
        '''
        Load credentials from the provided filepath if
        the file exists
        '''

        if not os.path.exists(self.__creds_filepath):
            raise Exception(
                f"Could not find saved credentials at path: '{self.__creds_filepath}'")

        with open(self.__creds_filepath, 'r') as file:
            cookies = json.loads(file.read())

            print("retrieved cookies")
            #print(cookies)

            self.__cookiejar = self.__create_cookiejar(
                cookies=cookies)

            self.__cookies = cookies

        return True

    def load_cookie_jar(
        self
    ):
        print('loading the cookie jar!')
        raw_cookies = self.__cookies
        #print(raw_cookies)

        if not empty(raw_cookies or []):
            raise Exception('Failed to capture driver cookies')

        # Convert the dictionary of cookie values returned from
        # the driver or loaded from stored credentials into a
        # requests cookiejar (derived from http.CookieJar used
        # by MFP client)
        print(f'Creating requests session cookiejar')
        session = requests.session()

        foreach(raw_cookies, lambda cookie: session.cookies.set(
            name=cookie.get('name'),
            value=cookie.get('value'))
        )

        print('setting auth cookie jar')
        self.__cookiejar = session.cookies


    def login(
        self,
        max_wait_time: int,
    ) -> bool:
        '''
        If `use_stored_credentials` is enabled:
        Attempt to fetch credentials from credential filepath and
        if the file does not exist then login using the webdriver
        and store the captured cookies

        If `use_stored_credentials` is not enabled::
        Login using a headless webdriver then capture driver cookies 
        in a `requests` session cookiejar

        `max_wait_time` : max time to wait for the driver to
        return a response
        '''

        print('starting webdriver login')

        try:
            self.__login(
                max_wait_time=max_wait_time)

            return True

        except TimeoutException as ex:
            self.__driver.save_screenshot('timeout.png')
            logger.exception(
                msg='Webdriver timeout exception')

            raise Exception(
                f'Login timed out, consider extending maximum wait times')

