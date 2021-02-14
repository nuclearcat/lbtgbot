#!/usr/bin/env python3
#pip3 install PyTelegramBotAPI==3.6.7
import telebot
import toml
import json
import hashlib

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

cfgopt = {}
cfgopt["users"] = {}
cfgopt["users"]["trusted"] = []

with open(r'bot.cfg') as file:
  cfgopt = toml.load(file, _dict=dict)
  print(cfgopt)

bot = telebot.TeleBot(cfgopt["auth"]["token"])

@bot.message_handler(commands=['start', 'help', 'trustme', 'userid', 'hackme','spam'])
def commands_handling(message):
    print(message)
    if(message.chat.type == "private"):
        if (message.text.startswith("/trustme")):
            print("trustme " + str(message.from_user.id))
            result = hashlib.sha256((cfgopt["auth"]["trustedseed"] + str(message.from_user.id)).encode('utf-8')).hexdigest()
            print("trustme request hash to match " + result)

    if(message.chat.type == "private"):
        if (message.text.startswith("/userid")):
            bot.reply_to(message, "Hey, your userid is:" + str(message.from_user.id))

    if(message.chat.type == "private"):
       if (message.text.startswith("/hackme") and cfgopt["auth"]["hackme"] == 1):
        if (not message.from_user.id in cfgopt["users"]["trusted"]):
          bot.reply_to(message, "Added you to trusted list")
          cfgopt["users"]["trusted"].append(message.from_user.id)
          with open('bot.cfg', 'w') as f:
              toml.dump(cfgopt, f)
        else:
            bot.reply_to(message, "You are already trusted")
       else:
        bot.reply_to(message, "What are you trying to do?")
    if(message.chat.type == "supergroup" and message.text.startswith("/spam")):
        
        #if (message.from_user.id in cfgopt["users"]["trusted"] and message.reply_to_message.from_user.id in cfgopt["users"]["trusted"]):
        if (message.from_user.id in cfgopt["users"]["trusted"]):
            user_id = message.from_user.id 
            user_name = message.from_user.first_name 
            mention = "["+user_name+"](tg://user?id="+str(user_id)+")"            
            bot.reply_to(message.reply_to_message, "Hey," + mention + " ,don't spam please!", parse_mode="Markdown")
            bot.delete_message(message.reply_to_message.chat.id, message.reply_to_message.message_id)

        bot.delete_message(message.chat.id, message.message_id)

@bot.message_handler(func=lambda message: message.forward_from_chat, content_types=["text", "photo", "video"])
def posts_from_channels(message):
    bot.reply_to(message, 'Hey, don\'t send this to our chat please')
    bot.delete_message(message.chat.id, message.message_id)
#    print(message)

@bot.message_handler(func=lambda message: message.forward_from_message_id, content_types=["text", "photo", "video"])
def posts_from_channels(message):
    bot.reply_to(message, 'Msg fwd heh?')


#@bot.message_handler(func=lambda m: True, content_types=["text", "photo", "video"])
#def handle_all(message):
#    print(type(message))
#    print(message)


bot.polling()
