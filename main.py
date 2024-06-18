import time
import os

import schedule
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from typing import List


load_dotenv()


class GoodMorningBot:
    def __init__(
            self, username: str, password: str, chat_name: str, driver_path: str,
            site_url: str
        ):
        self.username = username
        self.password = password
        self.chat_name = chat_name
        self.driver_path = driver_path
        self.site_url = site_url
        self.driver = None

    def login(self) -> None:
        """Выполняет вход на сайт с использованием заданных учетных данных."""
        try:
            username_input = self.driver.find_element(
                By.CSS_SELECTOR, 'input.login-inp[type="text"]'
            )
            password_input = self.driver.find_element(
                By.CSS_SELECTOR, 'input.login-inp[type="password"]'
            )
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            login_button = self.driver.find_element(By.CLASS_NAME, 'login-btn')
            login_button.click()
            time.sleep(3)
        except Exception as e:
            print(f'Ошибка входа: {e}')

    def send_good_morning_message(self) -> None:
        """
        Заходит на сайт, логинится, открывает нужный чат и отправляет сообщение
        'Доброго утра!', а затем вызывает функцию для поиска и лайка сообщений
        с приветствием.
        """
        service = Service(self.driver_path)
        self.driver = webdriver.Firefox(service=service)
        self.driver.get(self.site_url)
        time.sleep(3)

        self.login()
        chat_section = self.driver.find_element(
            By.ID, 'bx_left_menu_menu_im_messenger'
        )
        chat_section.click()
        time.sleep(3)
        desired_chat = self.driver.find_element(
            By.XPATH, f'//span[contains(text(), "{self.chat_name}")]'
        )
        desired_chat.click()
        time.sleep(5)
        self.driver.switch_to.active_element.send_keys('Доброго утра!')
        self.driver.switch_to.active_element.send_keys(Keys.RETURN)
        time.sleep(2)
        self.find_group_message()

    def find_group_message(self) -> None:
        """
        Ищет и обрабатывает сообщения за сегодняшний день, вызывая функцию для
        поиска утренних приветствий и установки лайков.
        """
        date_groups = self.driver.find_elements(
            By.CSS_SELECTOR, 'div.bx-im-message-list-date-group-title__text'
        )
        today_container = None
        for date_group in date_groups:
            if date_group.text.lower() == 'сегодня':
                today_container = date_group.find_element(
                    By.XPATH,
                    './ancestor::div[contains(@class, "bx-im-message-list-date-group__container")]'
                )
                break

        if today_container:
            opponent_messages = today_container.find_elements(
                By.CSS_SELECTOR,
                'div.bx-im-message-list-author-group__container.--opponent'
            )
            for group in opponent_messages:
                messages = group.find_elements(
                    By.CLASS_NAME, 'bx-im-message-default__container'
                )
                self.find_morning_and_like(messages)

    @staticmethod
    def replace_latin_with_cyrillic(text: str) -> str:
        """Заменяет латинские буквы в тексте на аналог кириллическим."""
        latin_to_cyrillic = {
            'A': 'А', 'B': 'В', 'E': 'Е', 'K': 'К', 'M': 'М', 'H': 'Н',
            'O': 'О', 'P': 'Р', 'C': 'С', 'T': 'Т', 'Y': 'У', 'X': 'Х',
            'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'c': 'с', 'y': 'у',
            'x': 'х'
        }
        return ''.join(latin_to_cyrillic.get(char, char) for char in text) if any(
            char in latin_to_cyrillic for char in text
        ) else text

    def find_morning_and_like(self, messages: List) -> None:
        """
        Ищет в сообщениях приветственные фразы и ставит лайки на
        соответствующие сообщения.
        """
        for message in messages:
            message_text = message.find_element(
                By.CSS_SELECTOR, 'div.bx-im-message-default-content__text'
            ).text.lower()
            message_text = self.replace_latin_with_cyrillic(message_text)
            if any(greeting in message_text for greeting in {
                'доброе утро', 'доброго', 'доброе', 'утро', 'утра',
                'morning', 'utro', 'utra', 'ytro', 'ytra', 'dobroe', 'dobrogo',
            }):
                like_button = message.find_element(
                    By.CSS_SELECTOR, 'div.bx-im-reaction-selector__selector'
                )
                like_button.click()

    def schedule_task(self) -> None:
        """
        Запускает планировщик для выполнения задачи с понедельника по пятницу
        в 8 утра.
        """
        schedule.every().monday.at("08:00").do(self.send_good_morning_message)
        schedule.every().tuesday.at("08:00").do(self.send_good_morning_message)
        schedule.every().wednesday.at("08:00").do(self.send_good_morning_message)
        schedule.every().thursday.at("08:00").do(self.send_good_morning_message)
        schedule.every().friday.at("08:00").do(self.send_good_morning_message)
        
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    bot = GoodMorningBot(
        username=os.getenv('USERNAME'),
        password=os.getenv('PASSWORD'),
        chat_name=os.getenv('CHAT_NAME'),
        driver_path=os.getenv('DRIVER_PATH'),
        site_url=os.getenv('SITE_URL')
    )
    bot.schedule_task()
