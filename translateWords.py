import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import Keys
from append_new_words import PathCreator
import json
import pprint


class WordsTranslation:
    """class to translate the words from container"""

    def __init__(self):
        self.browser_tools = Website_Translate_Helper()
        self.wooordHunt = WooordHunt()
        self.cambridge_dictionary = CambridgeDictionary()
        self.top_phonetics = TopPhonetics()
        self.pathCreator = PathCreator()
        self.path_to_containers = self.pathCreator.check_main_path()[3]
        self.wordHunt_words_translation = {}
        self.cambridge_word_translation = {}

    def wordTranslationInstruction(self, container_name: str):
        """instruction in what consequences functions should work."""
        words: list = self.get_container_list(container_name)
        self.translationLoopWordHunt(words)
        self.translationLoopCambridge(words)
        self.browser_tools.shutdown_browser()
        self.sort_and_merge_words()
        return self.wordHunt_words_translation

    def translationLoopWordHunt(self, words: list):
        """here we will do a loop for translation"""
        self.driver: webdriver = self.browser_tools.launch_browser()
        temp = {"transcription": None, "translation": None}
        for word in words:
            wordHuntTranslation: list = self.wooordHunt.translate(word, self.driver)
            if wordHuntTranslation is not None:
                self.wordHunt_words_translation[word] = {
                    "transcription": wordHuntTranslation[1],
                    "translation": wordHuntTranslation[0].split(", "),
                }
        else:
            print("translation done! (woordHunt)")

    def translationLoopCambridge(self, words: list):
        temp = {"translation": None}
        for word in words:
            translation: list = self.cambridge_dictionary.translate(word, self.driver)
            if translation is not None:
                self.cambridge_word_translation[word] = {
                    "translation": translation[0].split(", "),
                    "transcription": f"/{translation[1]}/",
                }
        else:
            print("translation done! (cambridgeDictionary)")

    def sort_and_merge_words(self):
        """here we'll compare to lists of different word translations and compare them."""
        for word, translation in self.cambridge_word_translation.items():
            translation_list = translation["translation"]
            full_translation_list = translation
            print(word, translation)
            for translation in translation_list:
                if word in self.wordHunt_words_translation.keys():
                    if (
                        translation
                        not in self.wordHunt_words_translation[word]["translation"]
                    ):
                        if type(translation) is list:
                            (
                                self.wordHunt_words_translation[word]["translation"]
                                + translation
                            )
                        else:
                            self.wordHunt_words_translation[word]["translation"].append(
                                translation
                            )
                else:
                    if type(translation) is list:
                        self.wordHunt_words_translation[word] = translation
                    else:
                        self.wordHunt_words_translation[word] = full_translation_list
        else:
            print("merge and sort succesfully done.")

    def _load_json(self) -> dict:
        with open(self.path_to_containers, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_container_list(self, container: str):
        """getting containers information."""
        containers_data: dict = self._load_json()
        return containers_data["containers"][0][container]  # container words list.


class Website_Translate_Helper:
    def __init__(self):
        self._browser_options()

    def launch_browser(self):
        print("launching browser")
        self.browser = webdriver.Chrome(self.options)
        return self.browser

    def _browser_options(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless=new")

    def get_to_url(self, url: str):
        print("directing to:", url)
        self.browser.get(url)
        status = WebDriverWait(self.browser, 20).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
        print("website loading:", status)

    def shutdown_browser(self):
        print("shutdowning browser")
        self.browser.quit()

    def get_word_status(self, word: str) -> bool:
        """checking if we can input word directly in url or not."""
        if " " in word:
            return False
        else:
            return True

    def connect(self, url):
        print("connecting to website not directly.")
        self.get_to_url(url)

    def connect_directly(self, url, word: str):
        print("connecting directly for word.")
        self.get_to_url(url + word)


class WooordHunt(Website_Translate_Helper):
    def __init__(self):
        super().__init__()
        self.url: str = "https://wooordhunt.ru"
        self.direct_url: str = "https://wooordhunt.ru/word/"

    def _get_search_bar(self):
        header: WebElement = self.browser.find_element(By.ID, "header")
        header_container = header.find_element(By.ID, "header_container")
        search_box = header_container.find_element(By.ID, "search_box")
        search_input_bar_helper = search_box.find_element(By.ID, "hunted_word_form")
        search_input_main = (
            search_input_bar_helper.find_element(By.TAG_NAME, "table")
            .find_element(By.TAG_NAME, "tbody")
            .find_element(By.TAG_NAME, "tr")
        )
        search_input = search_input_main.find_element(By.TAG_NAME, "td").find_element(
            By.TAG_NAME, "input"
        )
        search_sumbit_button = search_input_main.find_element(
            By.ID, "hunted_word_submit"
        )
        return [search_input, search_sumbit_button]

    def _get_transcription(self, trans_sound: WebElement):
        us_tr_sound = trans_sound.find_element(By.ID, "us_tr_sound")
        transcription = us_tr_sound.find_element(By.CLASS_NAME, "transcription")
        return transcription

    def _find_word_translation(self):
        try:
            container = WebDriverWait(self.browser, 20).until(
                EC.presence_of_element_located((By.ID, "container"))
            )
            content = WebDriverWait(container, 20).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            wd = WebDriverWait(content, 20).until(
                EC.presence_of_element_located((By.ID, "wd"))
            )
            wd_title = WebDriverWait(wd, 20).until(
                EC.presence_of_element_located((By.ID, "wd_title"))
            )
            trans_sound = WebDriverWait(wd_title, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "trans_sound"))
            )
            wd_content = WebDriverWait(wd, 20).until(
                EC.presence_of_element_located((By.ID, "wd_content"))
            )
            content_in_russian = WebDriverWait(wd_content, 3).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@id="content_in_russian"]')
                )
            )
            print("content in russian found.")
            transcription = self._get_transcription(trans_sound)
            translation = content_in_russian.find_element(By.CLASS_NAME, "t_inline_en")
            print("translation succesfully found!\nreturning...")
        except Exception as error:
            print("error occured during finding the translation (WoordHunt)")
            print(error)
            return None
        else:
            return [translation.text, transcription.text.replace("|", "/")]

    def _input_word_in_searchBar(
        self, search_input: WebElement, search_sumbit_button: WebElement, word: str
    ):
        search_input.send_keys(word)
        search_sumbit_button.click()

    def translate(self, word: str, driver: webdriver):
        print("wooordHunt!")
        self.browser = driver
        wordStatus: bool = self.get_word_status(word)
        if wordStatus:
            self.connect_directly(self.direct_url, word)
            translation_data: list | None = self._find_word_translation()
            if translation_data is not None:
                return translation_data
            else:
                return None
        else:
            self.connect(self.url)
            search_elements: list = self._get_search_bar()
            self._input_word_in_searchBar(
                search_input=search_elements[0],
                search_sumbit_button=search_elements[1],
                word=word,
            )
            translation = self._find_word_translation()
            return translation


class CambridgeDictionary(Website_Translate_Helper):
    def __init__(self):
        super().__init__()
        self.direct_url = "https://dictionary.cambridge.org/dictionary/english-russian/"

    def _find_word_translation(self):
        try:
            def_body = self.browser.find_element(By.CLASS_NAME, "def-body")
            translation = def_body.find_element(By.CLASS_NAME, "trans")
            pos_header = self.browser.find_element(
                By.CSS_SELECTOR, ".pos-header.dpos-h"
            )
            transcription = pos_header.find_element(
                By.CSS_SELECTOR, ".pron.dpron"
            ).find_element(By.CSS_SELECTOR, ".ipa.dipa.lpr-2.lpl-1")
        except Exception as error:
            print("error occured during getting translation (Cambridge!)")
            print(error)
            return None
        else:
            return [translation, transcription]

    def translate(self, word: str, driver):
        self.browser: webdriver = driver
        print("cambridge Dicrionary!")
        word = word.replace(" ", "-")
        self.connect_directly(self.direct_url, word)
        translation: list | None = self._find_word_translation()
        if translation is not None:
            return [translation[0].text, translation[1].text]
        else:
            return None


class TopPhonetics(Website_Translate_Helper):
    def __init__(self):
        self.url = "https://tophonetics.com/ru/"

    def get_transcription(word: str):
        pass


if __name__ == "__main__":
    wordTranslation = WordsTranslation()
    wordTranslation.wordTranslationInstruction("test")
