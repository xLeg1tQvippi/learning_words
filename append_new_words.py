import pathlib
import sqlite3
import os
import json
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import translateWords
import pandas as pd


class Menu:
    """main class that allows user to manage with"""

    def __init__(self):
        self.path_creator = PathCreator()
        paths: list = self.path_creator.check_main_path()
        self.db_manager = WordDatabaseManager(paths[2])
        self.container_manager = ContainerManager(paths[3])
        self.words_translation = translateWords.WordsTranslation()
        self.words_transcription = translateWords.WordTranscription()
        self.main_menu()

    def input_int(self, text):
        """process safe input"""
        while True:
            try:
                return int(input(text))
            except ValueError:
                print("Ошибка! Введите число.")

    def main_menu(self):
        """main menu"""
        print("Добро пожаловать в меню добавления слов!\nВыберите:")
        while True:
            print("\n1 - Добавить новые слова\n2 - Управление контейнерами\n0 - Выход")
            choice = self.input_int(">>> ")

            if choice == 1:
                self.addition_word_method()
            elif choice == 2:
                self.manage_containers()
            elif choice == 0:
                print("Выход из программы.")
                self.db_manager.close()
                break

    def manage_containers(self):
        """managing menu with containers"""
        while True:
            print(
                "\n1 - Создать контейнер\n2 - Показать контейнеры\n3 - Показать перевод последних слов\n4 - Перевести все слова из контейнера\n5 - Сохранить все переведенные слова\n0 - Назад"
            )
            choice = self.input_int(">>> ")
            if choice != 0:
                if choice == 1:
                    self.container_manager.create_new_container_chosing_method()
                elif choice == 2:
                    self.container_manager.show_containers_exists()
                elif choice == 3:
                    self.show_all_translated_words()
                elif choice == 4:
                    self.translate_words_from_container()
                elif choice == 5:
                    self.store_all_translated_words_to_DataBase()
            else:
                break

    def addition_word_method(self):
        """asking for user to choose the method of addition words."""
        chooseMethod = self.input_int(
            "Выберите метод добавления слов:\n1 - Ввода слов на перевод\n2 - Ввод слов с своим переводом\n0 - Вернуться в меню.\n>>>"
        )
        if chooseMethod != 0:
            if chooseMethod == 1:
                self.add_words_to_translate()
            elif chooseMethod == 2:
                self.add_words_with_own_translation()
        else:
            return

    def get_words_transcription(self, container_name: str) -> dict:
        """getting words transcription of own container word translation."""
        container: dict = self.words_transcription.main_instructions(container_name)
        return container

    def save_words_transcription_container(
        self, container_name: str, container_data: dict
    ):
        """saving data of transcription that was added to container."""
        containers: dict = self.container_manager._read_json()
        containers["containers_with_own_translation"][0][
            container_name
        ] = container_data
        self.container_manager._write_json(containers)
        print("transcriptions was succesfully saved.")

    def add_words_with_own_translation(self):
        """asking user to input the words with own translation."""
        containerStatus: bool = self.container_manager.check_if_containers_in_stock()
        if containerStatus:
            container_name: str = (
                self.container_manager.choose_container_with_own_translation()
            )
            if container_name is not None:
                status: bool = self.add_words_with_own_translation_loop(
                    container_name=container_name
                )
                if status:
                    container_data: dict = self.get_words_transcription(container_name)
                    self.save_words_transcription_container(
                        container_name, container_data
                    )
        else:
            return

    def add_words_with_own_translation_loop(self, container_name: str):
        """loop for inputing words to container with own translation of the word."""
        while True:
            print("Введите 0 чтобы сохранить и вернуться в меню.")
            word = input("Введите слово: ")
            if word == "0" or word == "" or word == " ":
                return True
            translations = input(f"Введите перевод слова {word} через запятую: ").split(
                ", "
            )
            if translations == ["0"] or translations == [""] or translations == [" "]:
                return True
            translation_list = [translation.strip() for translation in translations]
            self.container_manager.add_words_to_container_with_translation(
                container_name, word, translation_list
            )

    def add_words_to_translate(self):
        """adding words to a container"""
        containerStatus: bool = self.container_manager.check_if_containers_in_stock()
        if containerStatus:
            container_name: str = self.container_manager.choose_container()
            while True:
                word = input("Введите слово (0 - чтобы вернуться в меню.)\n>>>")
                if word != "0":
                    self.container_manager.add_words_to_container(container_name, word)
                    print(f"Слово '{word}' добавлено в контейнер '{container_name}'.")
                else:
                    break
        else:
            return

    def translate_words_from_container(self):
        """takes the words from choosen container and starting translating all of them."""
        try:
            containers_tempStatus: bool = (
                self.container_manager._check_containers_temp()
            )
            if containers_tempStatus:
                container_name: str = self.container_manager.choose_container()
                translated_data: dict = self.run_translating_words(container_name)
                self._store_translated_data(translated_data)
            else:
                raise ValueError(
                    "Закончите перевод слов // Сохраните все переведенные слова."
                )
        except ValueError as error:
            print(error)
        else:
            self.show_all_translated_words()

    def store_all_translated_words_to_DataBase(self):
        """storing data to a database."""
        container_name: str = self.container_manager.choose_container()
        translated_words_data: dict = self.get_translated_data()
        self.db_manager.create_table(container_name)
        for word, word_data in translated_words_data.items():
            transcription = word_data["transcription"]
            translation = ", ".join(word_data["translation"])
            self.db_manager.add_word(container_name, word, translation, transcription)
        else:
            print("saving data complete.")
            self.db_manager.close()
            self.container_manager._clean_containers_temp()

    def run_translating_words(self, container_name: str):
        """initializing words translation."""
        translatedWords = self.words_translation.wordTranslationInstruction(
            container_name
        )
        return translatedWords

    def _store_translated_data(self, translated_words: dict):
        """saving all translated data in containers_temp"""
        json_data = self.container_manager._read_json()
        json_data["containers_temp"] = list(translated_words)
        self.container_manager._write_json(json_data)

    def get_translated_data(self) -> dict:
        """takes the translated words data from containers temp."""
        try:
            json_data = self.container_manager._read_json()
            return json_data["containers_temp"][0]
        except Exception as error:
            print("На данный момент все переведенные слова сохранены в базу данных.")
            return False

    def show_all_translated_words(self):
        """shows all last translated words."""
        get_translated_words: dict = self.get_translated_data()
        if get_translated_words != False:
            pd.set_option("display.max_colwidth", None)
            df = pd.DataFrame.from_dict(get_translated_words, orient="index")
            df.index.name = "word"
            df["translation"] = df["translation"].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else x
            )
            df.style.set_properties(subset=["translation"], **{"text-align": "left"})
            print(df)


class ContainerManager:
    """class for managing containers with json."""

    def __init__(self, json_path):
        self.json_path = json_path
        self._ensure_json_exists()
        self.menu = object.__new__(Menu)

    def _ensure_json_exists(self):
        """creates json if not exists."""
        if not pathlib.Path(self.json_path).exists():
            print("Создаю JSON-файл контейнеров.")
            self._write_json(
                {
                    "containers": [],
                    "containers_with_own_translation": [],
                    "containers_temp": [],
                }
            )
            print("Создание JSON заверешено.")

    def _clean_containers_temp(self):
        """initiating cleaning containers temp."""
        json_data: dict = self._read_json()
        json_data["containers_temp"] = []
        self._write_json(json_data)

    def _write_json(self, data):
        """writes data to json"""
        with open(self.json_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print("Данные успешно сохранены. (JSON)")

    def _read_json(self):
        """reading json data"""
        with open(self.json_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_containers_with_own_translation(self) -> dict:
        """return containers with own translation"""
        return self._read_json()["containers_with_own_translation"]

    def get_containers(self):
        """returns the containers list"""
        return self._read_json()["containers"]

    def check_if_containers_in_stock(self):
        """checks if containers exists, (list with containers is not empty.)"""
        containers: list = self.get_containers()
        if not containers:
            print("Контейнеров нет! Сначала создайте контейнер.")
            return False
        else:
            return True

    def add_container(self, name: str) -> bool:
        """adds a new container."""
        name: dict = {name: []}
        data = self._read_json()
        if name not in data["containers"]:
            data["containers"].append(name)
            self._write_json(data)
            return True
        else:
            return False

    def add_container_with_own_translation(self, name: str) -> bool:
        """adds container with own translation"""
        var_name = "containers_with_own_translation"
        name: dict = {name: []}
        data = self._read_json()
        if name not in data[var_name]:
            data[var_name].append(name)
            self._write_json(data)
            return True
        else:
            return False

    def create_new_container_chosing_method(self):
        """asking for user to choose a creating container method"""
        containerMethod = self.menu.input_int(
            "Какой контейнер мы создаем?\n1 - Для перевода введенных слов\n2 - Для ввода слов с своим переводом\n0 - Назад\n>>>"
        )
        if containerMethod != 0:
            if containerMethod == 1:
                self.create_container_for_translation()
            elif containerMethod == 2:
                self.create_container_with_own_translation()
        else:
            return

    def create_container_with_own_translation(self):
        """creates container with own translation."""
        name = input("Введите имя нового контейнера с своим переводом: ")
        if self.add_container_with_own_translation(name):
            print(f"Контейнер '{name}' создан!")
        else:
            print("Ошибка! Контейнер с таким именем уже существует.")

    def create_container_for_translation(self):
        """creates a new container."""
        name = input("Введите имя нового контейнера: ")
        if self.add_container(name):
            print(f"Контейнер '{name}' создан!")
        else:
            print("Ошибка! Контейнер с таким именем уже существует.")

    def add_words_to_container_with_translation(
        self, container_name: str, word: str, translation: list
    ):
        containers: dict = self._read_json()
        initial_construction_data = {word: {"translation": translation}}
        for container in containers["containers_with_own_translation"]:
            if container_name in container:
                if container[container_name]:  # if container is not empty:
                    container[container_name][0][word] = {"translation": translation}
                else:
                    container[container_name].append(initial_construction_data)
            """ 
            should be look like:
            "container_name": [{
                word: {translation},
                word: {translation}
            }]
            """
        else:
            self._write_json(containers)

    def add_words_to_container(self, container_name: str, word: str):
        """add words to container."""
        containers: dict = self._read_json()
        for container in containers["containers"]:
            if container_name in container:
                container[container_name].append(word)
        else:
            self._write_json(containers)

    def show_containers_exists(self):
        """shows already existed containers name."""
        containers = self.get_containers()
        print("Существующие контейнеры:")
        print(", ".join([list(container.keys())[0] for container in containers]))

    def choose_container_with_own_translation(self) -> str | None:
        """helping tool to choose container (with own translation) returns container name."""
        while True:
            containers = self.get_containers_with_own_translation()
            containers = [list(container.keys())[0] for container in containers]
            print("Доступные контейнеры:", containers)
            container_completer = WordCompleter(containers, ignore_case=True)
            chooseContainer = prompt(
                "Выберите контейнер: ",
                completer=container_completer,
            )
            if chooseContainer not in containers:
                print("Ошибка! Такого контейнера нет.")
                return None
            else:
                return chooseContainer

    def choose_container(self) -> str | None:
        """helping tool to choose container. (returns the name if container choosing container exists.)"""
        while True:
            containers = self.get_containers()
            containers = [list(container.keys())[0] for container in containers]
            print("Доступные контейнеры:", containers)
            container_completer = WordCompleter(containers, ignore_case=True)
            chooseContainer = prompt(
                "Выберите контейнер: ",
                completer=container_completer,
            )
            if chooseContainer not in containers:
                print("Ошибка! Такого контейнера нет.")
                return None
            else:
                return chooseContainer

    def _check_containers_temp(self) -> bool:
        """checking if containers temp is empty to continue translating words."""
        json_data: dict = self._read_json()
        if json_data["containers_temp"]:
            if (
                input(
                    "Контейнер с переводом уже заполнен. Вы уверены что хотите перезаписать его?\n1 - Да\n2 - Нет\n>>>"
                )
                == "1"
            ):
                return True
            else:
                return False
        else:
            return True


class WordDatabaseManager:
    """class to manage words database."""

    def __init__(self, db_path):
        self.db_path = db_path
        print(self.db_path)
        self._connect()  # Проверяем соединение с БД

    def _connect(self):
        """creating connection with DataBase"""
        if not pathlib.Path(self.db_path).exists():
            print(f"No DataBase found, creaing new one..: {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def get_tables(self):
        """receiving all the containers (table) from DataBase"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()
        return [table[0] for table in tables]

    def create_table(self, table_name):
        """Creating new table for DataBase if not exists."""
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, word TEXT UNIQUE NOT NULL, transcription TEXT, translation TEXT)"
        self.cursor.execute(query)
        self.conn.commit()

    def add_word(self, table_name, word, translation, transcription):
        """adds a word into container."""
        query = f"""
    INSERT INTO {table_name} (word, transcription, translation)
    VALUES (?, ?, ?)
    ON CONFLICT(word) DO UPDATE 
    SET transcription = excluded.transcription, 
        translation = excluded.translation
"""
        self.cursor.execute(query, (word, transcription, translation))
        self.conn.commit()

    def covert_words_to_csv(self, container_name: str):
        """returns the words dict."""
        dataFrame = pd.read_sql(
            f"SELECT word, translation FROM {container_name}", self.conn
        )
        dataFrame.to_csv(
            "dictionary_files/quizlet_words.csv",
            index=False,
            header=["слово", "перевод"],
            encoding="utf-8",
            sep="\t",
        )
        print("words succesfully saved in csv format. // Database Manager.")

    def close(self):
        """closing connecton with DataBase."""
        self.conn.close()


class PathCreator:
    """class for creating paths and getting them to use in main menu."""

    def __init__(self):
        self.check_main_path()

    def check_main_path(self):
        db_path_file_name: str = "dictionary_files"
        conatiner_name: str = "containers.json"
        db_file_name = "words_database.db"
        parent_path = pathlib.Path(__file__).parent  # to learning_words.
        path_to_dictionary_files = pathlib.Path(
            parent_path / db_path_file_name
        )  # to dictionary_files.
        full_path_with_db = pathlib.Path(parent_path / db_path_file_name / db_file_name)
        full_path_wth_containers = pathlib.Path(
            parent_path / db_path_file_name / conatiner_name
        )
        return [
            parent_path,
            path_to_dictionary_files,
            full_path_with_db,
            full_path_wth_containers,
        ]


if __name__ == "__main__":
    menu = Menu()
