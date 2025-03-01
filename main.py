import json
import sqlite3
import os
import time
import testing_tools
import traceback
import append_new_words


class Main:
    def __init__(self):
        self.get_files_status()
        self.greet_and_redirect_instructions()

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

    """ greet and redirection """

    def greet_and_redirect_instructions(self):
        """here will be main instruction how does code will work // consequences."""
        self.greet()
        file_name: str = self.ask_to_pick_a_choice()
        self.redirect_to_file(file_name=file_name)

    def greet(self):
        """greeting user"""
        print("Добро пожаловать в программу для добавления слов и их изучения!")
        pass

    def ask_to_pick_a_choice(self):
        """asking user to choose the file if its append new words/learn words."""
        add_new_words = "append_new_words"
        while True:
            choice: str = self.input_int(
                "Выберите:\n1 - Добавление новых слов\n0 - Чтобы выйти из программы.\n>>>"
            )
            if choice != 0:
                if choice == 1:
                    self.redirect_to_file(add_new_words)
            else:
                break

    def redirect_to_file(self, file_name: str):
        """after user made a decision of choice we're redirecting user to its function/file."""
        launch_appending_words = "append_new_words"
        if file_name == launch_appending_words:
            addd_new_words = append_new_words.Menu()

    def launch_learn_words(self):
        """launching learning words file."""
        pass

    """ functions to check files (if they're created or not.) """

    def show_files_status(self, data: dict):
        for key, value in data.items():
            print(f"{key}: {value}")

    def write_new_supporting_files_data(
        self, json_name: str, file_name: str, status: bool, json_data: dict
    ):
        try:
            json_data[file_name] = status
            with open(json_name, "w", encoding="utf-8") as file:
                json.dump(json_data, file)
        except Exception as error:
            print(error)
        else:
            print(f"Данные о {file_name} успешно перезаписаны.")

    def create_dictionary_files_dir(self, dir: str):
        """creating directory for the DataBases and temp files for words."""
        os.makedirs(os.path.dirname(dir), exist_ok=True)

    def try_open_database(self, db_name) -> bool:
        creatingDir = self.create_dictionary_files_dir(db_name)
        try:
            if not os.path.exists(db_name):
                raise ValueError("database is not exists.")
        except Exception as error:
            return False
        else:
            return True

    def update_json_data(
        self, json_name: str, setting_name: str, setting_data: bool
    ) -> bool:
        json_data = self.load_json_data(json_name=json_name)
        print(json_data)
        json_data[setting_name] = setting_data
        print(json_data)
        self.save_json_data(json_name=json_name, json_data=json_data)

    def save_json_data(self, json_name, json_data) -> bool:
        with open(json_name, "w", encoding="utf-8") as file:
            data = json.dump(json_data, file)
        return True

    def load_json_data(self, json_name: str) -> dict:
        with open(json_name, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    def show_json_data(self, json_name: str):
        json_data = self.load_json_data(json_name)
        self.show_files_status(json_data)
        return json_data

    def get_files_status(self):
        try:
            files_json_name = "settings.json"
            words_database = "words_database"
            db_name = "words_database.db"
            db_path_name = "dictionary_files/"
            full_db_path = f"{db_path_name+db_name}"

            testDB = self.try_open_database(full_db_path)
            print("testDB:", testDB)
            if not testDB:
                updateDB = self.update_json_data(
                    json_name=files_json_name,
                    setting_name=words_database,
                    setting_data=testDB,
                )
                if updateDB:
                    print(f"{files_json_name} succesfully updated.")

            data = self.show_json_data(files_json_name)

            if not data[words_database]:
                """initialize creating database."""
                db_path = f"{db_path_name + db_name}"
                status_db: bool = self.create_words_database(full_db_path)
                if status_db:
                    self.write_new_supporting_files_data(
                        files_json_name, words_database, status_db, data
                    )

        except Exception as error:
            testing_var = testing_tools.Testing()
            testing_var.explain_exception(
                error,
                traceback_info=traceback.format_exc(),
            )

        else:
            input("enter to clear history.")
            self.clear_console_history()

    def create_words_database(self, db_name: str):
        with sqlite3.connect(db_name) as conn:
            pass
        print("База данных для слов создана.")
        return True

    """ cleaning console after preparing status """

    def clear_console_history(self):
        print("cleaning console history...")
        time.sleep(1)
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")


if __name__ == "__main__":
    Main()
