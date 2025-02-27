import traceback
import json


class Testing:
    def __init__(self):
        pass

    @staticmethod
    def decorator_test(func):
        def wrapper(*args, **kwargs):
            print(
                f"launching function: {func.__name__} with args: {args}, kwargs: {kwargs}"
            )
            result = func(*args, **kwargs)
            print(f"function {func.__name__} finished with result: {result}")

        return wrapper

    def get_debug_data(self):
        json_name = "learning_words/settings.json"
        with open(json_name, "r") as file:
            data = json.load(file)
        return data

    def explain_exception(self, error: str, traceback_info: str):
        print(r"////", "\033[4m - Exception - \033[0m", r"\\\\")
        print(f"Caught error: {error}")
        json_data = self.get_debug_data()
        if json_data["detailed_debug"]:
            print(f"\033[4mdetailed information\033[0m: \n{traceback_info}")
