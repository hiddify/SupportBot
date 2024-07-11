#!/usr/bin/python

import telebot
import logging
from .hiddifyapi import HiddifyApi
from telebot import TeleBot,ExceptionHandler
from telebot import handler_backends

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.


class MyExceptionHandler(ExceptionHandler):
    async def handle(self, exception):
        logger.error(exception)

bot:TeleBot = TeleBot('', exception_handler=MyExceptionHandler(),use_class_middlewares=True)

class Middleware(handler_backends.BaseMiddleware):
    def __init__(self):
        self.update_types = ['message'] 
        pass
    def pre_process(self, message, data):
        data['lang']=message.from_user.language_code
        # data['lang']="en"
        data['hapi']=HiddifyApi('http://localhost:9000/','')
    def post_process(self, message, data, exception):
        pass


bot.setup_middleware(Middleware()) 
