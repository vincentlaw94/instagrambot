from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import os
import time
from utility_methods.utility_methods import *
import re
import random
from helper import *


class InstagramBot:
    # get_followers
    # comment
    # follow
    # nav to username
    #
    def __init__(self, username=None, password=None):
        PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
        DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")
        self.driver = webdriver.Chrome(executable_path=DRIVER_BIN)
        self.username = config['IG_AUTH']['USERNAME']
        self.password = config['IG_AUTH']['PASSWORD']

        self.login_url = config['IG_URLS']['LOGIN']
        self.nav_user_url = config['IG_URLS']['NAV_USER']
        self.get_tag_url = config['IG_URLS']['SEARCH_TAGS']

        self.log_in = False
        self.following = []
        self.followers = []

    def login(self):
        """
        logs a user into Instagram via web portal
        """

        self.driver.get(self.login_url)
        time.sleep(1)
        username_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="loginForm"]/div[1]/div[1]/div/label/input'))
        )
        password_input = self.driver.find_element_by_xpath(
            '//*[@id="loginForm"]/div[1]/div[2]/div/label/input')

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)

        login_btn = self.driver.find_element_by_xpath(
            '//*[@id="loginForm"]/div[1]/div[3]/button')
        login_btn.click()
        savedInfoBtn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="react-root"]/section/main/div/div/div/div/button'))
        )
        savedInfoBtn.click()
        turnOffNotification = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[4]/div/div/div/div[3]/button[2]')))
        turnOffNotification.click()

    def contest_entry(self, post_url):
        self.driver.get(post_url)

        # parse description and find all username handle to follow
        description = self.driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span')
        regrex = re.compile(r'@([A-Za-z0-9_]+)')
        contest_follows = list(set(regrex.findall(description.text)))

        # select comment text area
        commentSection = ui.WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea.Ypffh")))
        self.driver.execute_script(
            "arguments[0].scrollIntoView(true);", commentSection)

        # like contest post
        like_btn = self.driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[1]/span[1]/button')

        liked = like_btn.find_elements_by_tag_name(
            'svg')[0].get_attribute("aria-label")

        if liked == "Like":
            like_btn.click()
        # follow contest user
        for user in contest_follows:
            if user not in self.followers:
                self.driver.get(self.nav_user_url.format(user))
                follow_btn = self.driver.find_element_by_xpath(
                    '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button')
                follow_btn.click()
        # post mention following users
        self.driver.get(post_url)
        shuffled_followers = random.sample(self.followers, len(self.followers))
        print(shuffled_followers)
        for user in shuffled_followers:

            try:
                commentSection = ui.WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea.Ypffh")))

                commentSection.send_keys('@'+user)
                post_btn = self.driver.find_element_by_xpath(
                    '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[3]/div[1]/form/button')
                post_btn.click()
                time.sleep(random.randint(0, 60))
            except Exception:
                time.sleep(random.randint(3, 4))

    def infinite_scroll(self, src=None):
        """
        Scrolls to the bottom of a users page to load all of their media
        Returns:
            bool: True if the bottom of the page has been reached, else false
        """

        SCROLL_PAUSE_TIME = 0.2

        self.driver.execute_script(
            'arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', src)

        time.sleep(SCROLL_PAUSE_TIME)

        self.new_height = self.driver.execute_script(
            "return arguments[0].scrollHeight", src)

        self.totalHeight = self.driver.execute_script(
            "return arguments[0].offsetHeight + arguments[0].scrollTop", src)
        if self.totalHeight == self.new_height:
            return True

        return False

    def get_following_list(self):
        # log in to accounts page
        self.driver.get(self.nav_user_url.format(self.username))
        time.sleep(1)
        following_btn = self.driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a')
        following_btn.click()
        time.sleep(1)
        # self.driver.find_element_by_xpath(
        #     '/html/body/div[5]/div/div/div/div/div/div[3]/a').click()

        # get following list
        # time.sleep(3)
        # following_btn1 = self.driver.find_element_by_xpath(
        #     '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]')
        # following_btn1.click()
        time.sleep(1)

        # scroll to the bottom of following modal
        following_list = self.driver.find_element_by_xpath(
            '/html/body/div[5]/div/div/div[2]')
        finished = False
        while not finished:
            finished = self.infinite_scroll(following_list)

        following_users = following_list.find_elements_by_tag_name('a')
        for user in following_users:
            self.following.append(user.text)

        self.followers = removeElements(self.following, '')

    def quit(self):
        self.driver.quit()


if __name__ == '__main__':
    config_file_path = './config.ini'
    logger_file_path = './bot.log'
    config = init_config(config_file_path)
    logger = get_logger(logger_file_path)
    bot = InstagramBot()
    try:
        bot.login()
        bot.get_following_list()

        bot.contest_entry('https://www.instagram.com/p/CJppXzasXIT/')

    finally:
        bot.quit()
        print('done')
