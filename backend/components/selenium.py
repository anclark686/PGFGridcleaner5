from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException, ElementNotInteractableException
import time
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path

chrome_options = webdriver.ChromeOptions() 

   
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])

bot = webdriver.Chrome(options=chrome_options)

pc_logged = False

def login():
    fv_search = "http://fvscheduling.focusvision.local/FVScheduling/Search.htm"
    bot.get(fv_search)


def pc_login(pnum):
    global pc_logged

    fvss = "http://fvscheduling.focusvision.local/FVScheduling/Project.htm?ProjectId="
    fvpc = "https://online.focusvision.com/FVPC/default.aspx?Projectid="

    what_page = bot.current_url
    if what_page != fvss + pnum:
        bot.get(fvss + pnum)

    try:
        proj_menu = bot.find_element(By.CSS_SELECTOR, "#search + li")
        proj_menu.click()
        time.sleep(1)
        pc_gateway = bot.find_element(By.ID, "projectCentral")
        pc_gateway.click()
        time.sleep(3)
        bot.switch_to.window(bot.window_handles[1])
        time.sleep(1)
        pc_logged = True
    except ElementNotInteractableException as err:
        pc_login(pnum)
    
    return pc_logged

def get_bot_pclog():
    return [bot, pc_logged]