from selenium import webdriver
import os
import time
from utility_methods.utility_methods import *
import random

class InstagramBot:
    # get_followers
    # comment
    # follow
    # nav to username
    #
    def __init__(self,username=None,password=None):
        self.driver = webdriver.Chrome(config['ENVIRONMENT']['CHROMEDRIVER_PATH'])
        self.username = config['IG_AUTH']['USERNAME']
        self.password = config['IG_AUTH']['PASSWORD']

        self.login_url =config['IG_URLS']['LOGIN']
        self.nav_user_url = config['IG_URLS']['NAV_USER']
        self.get_tag_url = config['IG_URLS']['SEARCH_TAGS']
        self.post_url = config['IG_URLS']['POST_LINK']

        self.log_in = False
        self.following=[]
        self.followers=[]

    def login(self):
        """
        logs a user into Instagram via web portal
        """

        self.driver.get(self.login_url)
        time.sleep(1)
        username_input = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[2]/div/label/input')
        password_input = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[3]/div/label/input')

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)

        login_btn = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button')
        login_btn.click()

    def infinite_scroll(self, src=None):
            """
            Scrolls to the bottom of a users page to load all of their media
            Returns:
                bool: True if the bottom of the page has been reached, else false
            """

            SCROLL_PAUSE_TIME = 0.2

            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', src)

            time.sleep(SCROLL_PAUSE_TIME)

            self.new_height = self.driver.execute_script("return arguments[0].scrollHeight",src)

            self.totalHeight = self.driver.execute_script("return arguments[0].offsetHeight + arguments[0].scrollTop",src)
            if self.totalHeight == self.new_height:
                return True

            return False

    def get_following_list(self):
        #log in to accounts page
        self.driver.get(self.nav_user_url.format(self.username))
        following_btn  = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a')
        following_btn.click()

        self.driver.find_element_by_xpath('/html/body/div[5]/div/div/div/div/div/div[3]/a').click()
        time.sleep(1)
        username_input = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[2]/div/label/input')
        password_input = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[3]/div/label/input')

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)

        login_btn = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button')
        login_btn.click()

        #get following list
        time.sleep(2)
        following_btn1 = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]')
        following_btn1.click()
        time.sleep(1)

        #scroll to the bottom of following modal
        following_list = self.driver.find_element_by_xpath('/html/body/div[4]/div/div[2]')
        finished = False
        while not finished:
            finished=self.infinite_scroll(following_list)

        print("Getting Following list")
        following_users =following_list.find_elements_by_tag_name('a')
        for user in following_users:
            self.following.append(user.text)



        

if __name__ == '__main__':
    config_file_path = './config.ini'
    logger_file_path = './bot.log'
    config = init_config(config_file_path)
    logger = get_logger(logger_file_path)

    bot = InstagramBot()

    bot.get_following_list()
