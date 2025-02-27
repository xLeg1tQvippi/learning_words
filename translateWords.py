import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import Keys


class WordTranslation:
    """class to translate the words from container"""

    def __init__(self):
        self.woordhunt_url = "https://wooordhunt.ru"
        self.cambridge_dictionary_url = (
            "https://dictionary.cambridge.org/dictionary/english-russian/"
        )
        self.top_phonetics_url = "https://tophonetics.com/ru/"

    def wordTranslationInstruction(self):
        """instruction in what consequences functions should work."""
