from hiddifypanel_bot import bot,hiddifyapi
from telebot.types import ReactionTypeEmoji,Message



def set_reaction(message:Message,emoji:str="👍"):
    return bot.set_message_reaction(message.chat.id, message.id, [ReactionTypeEmoji(emoji)], is_big=False)