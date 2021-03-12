#!/usr/bin/env python3
#pip3 install PyTelegramBotAPI==3.6.7
#https://github.com/eternnoir/pyTelegramBotAPI
import telebot
import toml
import json
import hashlib
import time
import logging

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

logging.basicConfig(filename='bot.log', level=logging.INFO)

bot = telebot.TeleBot(cfgopt["auth"]["token"])

@bot.message_handler(commands=['start', 'help', 'trustme', 'userid', 'hackme', 'spam', 'nofight', 'debug'])
def commands_handling(message):
    print(message)
    if(message.chat.type == "private"):
        if (message.text.startswith("/start")):
            bot.reply_to(message, cfgopt["users"]["startmsg"])

#        if (message.text.startswith("/trustme")):
#            print("trustme " + str(message.from_user.id))
#            result = hashlib.sha256((cfgopt["auth"]["trustedseed"] + str(message.from_user.id)).encode('utf-8')).hexdigest()
#            print("trustme request hash to match " + result)

        if (message.text.startswith("/userid")):
            bot.reply_to(message, "Hey, your userid is:" + str(message.from_user.id))

        if (message.text.startswith("/debug")):
            print(message)

#        if (message.text.startswith("/trustme") and cfgopt["auth"]["trustme"] == 1 and message.from_user.id not in cfgopt["users"]["newmembers"]):
#         if (not message.from_user.id in cfgopt["users"]["trusted"]):
#          bot.reply_to(message, "Hello Master, i added you to trusted list")
#          cfgopt["users"]["trusted"].append(message.from_user.id)
#          with open('bot.cfg', 'w') as f:
#              toml.dump(cfgopt, f)
#         else:
#            bot.reply_to(message, "You are already trusted or bot have bug")

    if(message.chat.type == "supergroup" and message.text.startswith("/spam")):
        if (message.from_user.id in cfgopt["users"]["trusted"] and message.reply_to_message is not None):
            logging.info('ADMIN: User '+str(message.from_user.id)+' marked message "'+message.reply_to_message.text+'" as spam')
            user_id = message.reply_to_message.from_user.id
            user_name = message.reply_to_message.from_user.first_name
            mention = "["+user_name+"](tg://user?id="+str(user_id)+")"
            bot.reply_to(message.reply_to_message, "Hey," + mention + " ," + cfgopt["lang"]["nospamplease"], parse_mode="Markdown")
            bot.delete_message(message.reply_to_message.chat.id, message.reply_to_message.message_id)
            bot.restrict_chat_member(message.reply_to_message.chat.id, message.reply_to_message.from_user.id, until_date=time.time()+ cfgopt["misc"]["spam_mute_duration"])
        bot.delete_message(message.chat.id, message.message_id)

    if(message.chat.type == "supergroup" and message.text.startswith("/nofight")):
        #if (message.from_user.id in cfgopt["users"]["trusted"] and message.reply_to_message.from_user.id in cfgopt["users"]["trusted"]):
        if (message.from_user.id in cfgopt["users"]["trusted"] and message.reply_to_message is not None):
            if (time.time() - message.reply_to_message.date < cfgopt["misc"]["fightage"]):
              user_id = message.reply_to_message.from_user.id 
              user_name = message.reply_to_message.from_user.first_name 
              mention = "["+user_name+"](tg://user?id="+str(user_id)+")"            
              bot.reply_to(message.reply_to_message, "CALM DOWN OR YOU WILL BE SHOT BY ROBOTIC OVERLORD! Some messages are deleted, users temporary muted (but it is all in log), don't fight please!", parse_mode="Markdown")
              bot.delete_message(message.reply_to_message.chat.id, message.reply_to_message.message_id)
              bot.restrict_chat_member(message.reply_to_message.chat.id, message.reply_to_message.from_user.id, until_date=time.time()+ 300)

        bot.delete_message(message.chat.id, message.message_id)


#@bot.message_handler(func=lambda message: message.forward_from_chat, content_types=["text", "photo", "video"])
#def posts_from_channels(message):
#    bot.reply_to(message, 'Hey, don\'t send this to our chat please')
#    bot.delete_message(message.chat.id, message.message_id)


#@bot.message_handler(func=lambda message: message.forward_from_message_id, content_types=["text", "photo", "video"])
#def posts_from_channels(message):
#    bot.reply_to(message, 'Msg fwd heh?')


# TODO: Check new member id to estimate age?
# TODO: Disable for unconfirmed members anything else than plain text messages?
# TODO: Handle new members send picture spam? (test)
@bot.message_handler(content_types=[
    "new_chat_members"
])
def new_chat_member_handling(message):
    bot.reply_to(message, cfgopt["lang"]["welcome"])
    cfgopt["users"]["newmembers"].append(message.from_user.id)
    with open('bot.cfg', 'w') as f:
      toml.dump(cfgopt, f)


@bot.message_handler(func=lambda m: True, content_types=["text", "photo", "video"])
def handle_all(message):
    if (message.from_user.id in cfgopt["users"]["newmembers"] and message.entities != None and len(message.entities) > 0):
      user_id = message.from_user.id 
      user_name = message.from_user.first_name 
      mention = "["+user_name+"](tg://user?id="+str(user_id)+")"            

      bot.reply_to(message, cfgopt["lang"]["nolinks"])
      bot.delete_message(message.chat.id, message.message_id)
      bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time()+ 60)

#    print("DEBUG:")
#    print(message)
#    bot.reply_to(message, 'Debug, entities: ' + str(len(message.entities)))

try:
  bot.polling(none_stop=True)
except Exception as e:
        logger.error(e)
        time.sleep(5)

