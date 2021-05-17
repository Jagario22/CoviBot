import logging

import requests
from bottle import Bottle, response, request as bottle_request
from bot import therapist as th

greeting_message = "Hello. I'm CoviBot."

therapist = th.Therapist()
therapist.load('coronavirus.txt')
logging.info(therapist.initial())


class BotHandlerMixin:
    BOT_URL = None

    def get_chat_id(self, data):
        """
        Method to extract chat id from telegram request.
        """
        chat_id = data['message']['chat']['id']

        return chat_id

    def get_message(self, data):
        """
        Method to extract message id from telegram request.
        """
        message_text = data['message']['text']

        return message_text

    def send_message(self, prepared_data):
        """
        Prepared data should be json which includes at least `chat_id` and `text`
        """
        message_url = self.BOT_URL + 'sendMessage'
        requests.post(message_url, json=prepared_data)


class TelegramBot(BotHandlerMixin, Bottle):

    def __init__(self, *args, **kwargs):
        super(TelegramBot, self).__init__()
        self.route('/', callback=self.post_handler, method="POST")

    def prepare_data_for_answer(self, data):
        message = self.get_message(data)
        print(message)

        return self.process_command(message, data)

    def process_command(self, message, data):
        if message == "/start":
            answer = greeting_message
        else:
            answer = therapist.respond(message)
            print(answer)
            answer.encode(encoding='UTF-8', errors='strict')
        chat_id = self.get_chat_id(data)
        json_data = {
            "chat_id": chat_id,
            "text": answer,
        }

        return json_data

    def post_handler(self):
        data = bottle_request.json
        answer_data = self.prepare_data_for_answer(data)
        self.send_message(answer_data)

        return response


if __name__ == '__main__':
    app = TelegramBot()
    app.run(host='localhost', port=8080)
