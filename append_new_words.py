import pathlib
import sqlite3
import os
import json
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import translateWords


class maenu:
    def __init__(self):
        self.db_name = "\\words_database.db"
        self.container_name: str = "\\containers.json"
        paths = self.get_words_database_path()
        # self.create_container_json()
        self.full_path_without_db = paths[0]
        self.full_path_with_db = paths[1]

        self.check_container_existance()
        input("-")
        self.menu()

    def input_int(self, text):
        """Функция для проверки введенных данных во избежании ошибок."""
        while True:
            try:
                status = int(input(text))
            except:
                print("Введите число")
                continue
            else:
                return status

    def get_words_database_path(self):
        root_file_name: str = pathlib.Path(__file__).parent
        print(root_file_name)
        full_path_without_db: str = str(root_file_name) + "\\dictionary_files"
        full_path_with_db: str = full_path_without_db + self.db_name
        return [full_path_without_db, full_path_with_db]

    def menu(self):
        while True:
            print(
                "1 - Чтобы добавить новые слова\n2 - Чтобы изменить язык ввода/перевода\n0 - Вернуться обратно."
            )
            choice = self.input_int(">>>")
            if choice != 0:
                if choice == 1:
                    writeWordsInstrStatus: bool = self.write_words_instructions()
                    if not writeWordsInstrStatus:
                        pass
                    else:
                        continue
            else:
                break

    def load_container_json(self, path: str):
        pass

    def get_tables(self):
        """Получает список всех таблиц в БД"""
        try:
            with sqlite3.connect(self.full_path_with_db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
        except Exception as error:
            print("error", error)
        else:
            return [table[0] for table in tables]  # taking names from tuple

    def check_container_existance(self):
        full_path_to_container = self.full_path_without_db + self.container_name
        covnert_container_path = pathlib.Path(full_path_to_container)
        if not os.path.exists(covnert_container_path):
            print("creating json container file.")
            creatingJsonContainerStatus = self.create_container_json(
                covnert_container_path
            )
            if creatingJsonContainerStatus:
                print("creating successfully done.")
                return True
        else:
            print("json container already exists.")
            return None

    def create_container_json(self, full_path_with_container) -> bool:
        try:
            with open(full_path_with_container, "w", encoding="utf-8") as file:
                json.dump({"containers": [], "containers_temp_data": []}, file)
        except Exception as error:
            print(error)
            return False
        else:
            return True

    def add_new_container(self):
        pass

    def show_containers_not_found(self):
        pass

    def ask_for_user_to_create_container(self) -> bool:
        choice = self.input_int(
            "Введите:\n1 - Чтобы создать новый контейнер\n2 - Чтобы вернуться в меню.\n>>>"
        )
        if choice != 0:
            if choice == 1:
                return True
        else:
            return False

    def choose_word_container(self):
        containers = self.get_tables()
        if not containers:  # if tables containers are empty. (containers are empty.)
            createContainerStatus: bool = self.show_containers_not_found()
            if not createContainerStatus:
                creatingStatus: bool = (
                    self.create_container_json()
                )  # creating json container.
            else:
                return False  # returning back to menu.
        else:
            print(True)  # meanwhile its print (for debugging)

    def write_words_instructions(self):
        """main instruction in what sequences function should be followed."""
        container: bool = self.choose_word_container()
        if not container:
            pass
        else:
            return False  # return to menu


class Menu:
    """main class that allows user to manage with"""

    def __init__(self):
        self.path_creator = PathCreator()
        paths: list = self.path_creator.check_main_path()
        self.db_manager = WordDatabaseManager(paths[2])
        self.container_manager = ContainerManager(paths[3])
        self.words_translation = translateWords.WordsTranslation()
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
        while True:
            print("\n1 - Добавить новые слова\n2 - Управление контейнерами\n0 - Выход")
            choice = self.input_int(">>> ")

            if choice == 1:
                self.add_words()
            elif choice == 2:
                self.manage_containers()
            elif choice == 0:
                print("Выход из программы.")
                self.db_manager.close()
                break

    def add_words(self):
        """adding words to a container"""
        containers: list = self.container_manager.get_containers()
        if not containers:
            print("Контейнеров нет! Сначала создайте контейнер.")
            return

        container_completer = WordCompleter(
            list(containers[0].keys()), ignore_case=True
        )
        print("Выберите контейнер:", *list(containers[0].keys()))
        container = prompt("Введите имя контейнера: ", completer=container_completer)

        if container not in containers[0].keys():
            print("Ошибка! Такого контейнера нет.")
            return
        else:
            while True:
                word = input("Введите слово (0 - чтобы вернуться в меню.)\n>>>")
                if word != "0":
                    self.container_manager.add_words_to_container(container, word)
                    print(f"Слово '{word}' добавлено в контейнер '{container}'.")
                else:
                    break

    def manage_containers(self):
        """managing menu with containers"""
        while True:
            print(
                "\n1 - Создать контейнер\n2 - Показать контейнеры\n3 - Перевести слова из контейнера\n0 - Назад"
            )
            choice = self.input_int(">>> ")

            if choice == 1:
                name = input("Введите имя нового контейнера: ")
                if self.container_manager.add_container(name):
                    print(f"Контейнер '{name}' создан!")
                else:
                    print("Ошибка! Контейнер с таким именем уже существует.")
            elif choice == 2:
                print(
                    "Существующие контейнеры:", self.container_manager.get_containers()
                )
            elif choice == 3:
                containers = self.container_manager.get_containers()
                container_completer = WordCompleter(
                    list(containers[0].keys()), ignore_case=True
                )
                chooseContainer = prompt(
                    "Выберите контейнер для перевода:", completer=container_completer
                )
                print("Запускаем перевод слов.")
                translation = self.words_translation.wordTranslationInstruction(chooseContainer)
                print("Перевод слов завершен")
                print(translation)
            elif choice == 0:
                break


class ContainerManager:
    """class for managing containers with json."""

    def __init__(self, json_path):
        self.json_path = json_path
        self._ensure_json_exists()

    def _ensure_json_exists(self):
        """creates json if not exists."""
        if not pathlib.Path(self.json_path).exists():
            print("Создаю JSON-файл контейнеров.")
            self._write_json({"containers": [], "containers_temp": []})

    def _write_json(self, data):
        """writes data to json"""
        with open(self.json_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def _read_json(self):
        """reading json data"""
        with open(self.json_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_containers(self):
        """returns the containers list"""
        return self._read_json()["containers"]

    def add_container(self, name):
        """adds a new container."""
        name: dict = {name: []}
        data = self._read_json()
        if name not in data["containers"]:
            data["containers"].append(name)
            self._write_json(data)
            return True
        return False

    def add_words_to_container(self, container_name: str, word: str):
        containers: dict = self._read_json()
        containers["containers"][0][container_name].append(word)
        self._write_json(containers)


class WordDatabaseManager:
    """class to manage words database."""

    def __init__(self, db_path):
        self.db_path = db_path
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
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, word TEXT, translation TEXT, transcription TEXT)"
        self.cursor.execute(query)
        self.conn.commit()

    def add_word(self, table_name, word, translation, transcription):
        """adds a word into container."""
        query = f"INSERT INTO {table_name} (word, translation, transcription) VALUES (?, ?, ?)"
        self.cursor.execute(query, (word, translation, transcription))
        self.conn.commit()

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
