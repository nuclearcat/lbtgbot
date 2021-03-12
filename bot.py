#!/usr/bin/env python3
#pip3 install PyTelegramBotAPI==3.6.7
#https://github.com/eternnoir/pyTelegramBotAPI
import telebot
import toml
import json
import hashlib
import time
import logging

def mention_string(message):
      user_id = message.from_user.id 
      user_name = message.from_user.first_name 
      mention = "["+user_name+"](tg://user?id="+str(user_id)+")"
      return mention

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

cfgopt = {}
cfgopt["users"] = {}
cfgopt["users"]["admins"] = []
cfgopt["users"]["trusted"] = []
cfgopt["users"]["normal"] = []
cfgopt["misc"] = {}
cfgopt["misc"]["group"] = 0

with open(r'bot.cfg') as file:
  cfgopt = toml.load(file, _dict=dict)
  print(cfgopt)

logging.basicConfig(filename='bot.log', level=logging.INFO)

bot = telebot.TeleBot(cfgopt["auth"]["token"])

@bot.message_handler(commands=['start', 'help', 'trustme', 'userid', 'hackme', 'spam', 'nofight', 'debug', 'human'])
def commands_handling(message):
#    print(message)
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

#{'user': {'id': 238455107, 'is_bot': False, 'first_name': 'Denys', 'username': 'nuclearcatlb', 'last_name': 'Fedoryshchenko', 'language_code': 'en'}, 'status': 'creator', 'until_date': None, 'can_be_edited': None, 'can_change_info': None, 'can_post_messages': None, 'can_edit_messages': None, 'can_delete_messages': None, 'can_invite_users': None, 'can_restrict_members': None, 'can_pin_messages': None, 'can_promote_members': None, 'can_send_messages': None, 'can_send_media_messages': None, 'can_send_other_messages': None, 'can_add_web_page_previews': None}

    with open('bot.cfg', 'w') as f:
      toml.dump(cfgopt, f)


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
        if (message.from_user.id in cfgopt["users"]["trusted"] and message.reply_to_message is not None):
            if (time.time() - message.reply_to_message.date < cfgopt["misc"]["fightage"]):
              user_id = message.reply_to_message.from_user.id 
              user_name = message.reply_to_message.from_user.first_name 
              mention = "["+user_name+"](tg://user?id="+str(user_id)+")"            
              bot.reply_to(message.reply_to_message, cfgopt["lang"]["nofight"], parse_mode="Markdown")
              bot.delete_message(message.reply_to_message.chat.id, message.reply_to_message.message_id)
              bot.restrict_chat_member(message.reply_to_message.chat.id, message.reply_to_message.from_user.id, until_date=time.time()+ 300)

        bot.delete_message(message.chat.id, message.message_id)

    if(message.chat.type == "supergroup" and message.text.startswith("/human")):
      logging.info('ADMIN: User '+str(message.from_user.id)+' marked person "'+mention_string(message.reply_to_message)+'" as human')
      cfgopt["users"]["newmembers"].remove(message.reply_to_message.from_user.id)
      with open('bot.cfg', 'w') as f:
        toml.dump(cfgopt, f)

      bot.delete_message(message.chat.id, message.message_id)


# TODO: Check new member id to estimate age?
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

    
    if(message.chat.type == "supergroup"):
      if (cfgopt["misc"]["group"] == 0):
        cfgopt["misc"]["group"] = message.chat.id
        with open('bot.cfg', 'w') as f:
         toml.dump(cfgopt, f)
        bot.reply_to(message.reply_to_message, "Bot assigned to this group", parse_mode="Markdown")
      else:
        if (cfgopt["misc"]["group"] != message.chat.id):
          bot.reply_to(message, "This bot doesnt belong to this group", parse_mode="Markdown")
          return


    if (len(cfgopt["users"]["admins"]) == 0):
           info = bot.get_chat_administrators(message.chat.id)
           for i in info:
            #print(i)
            #print(i.user.id)
            cfgopt["users"]["admins"].append(i.user.id)
            cfgopt["users"]["trusted"].append(i.user.id)
           
            with open('bot.cfg', 'w') as f:
             toml.dump(cfgopt, f)

           bot.reply_to(message, "Bot initial setup completed", parse_mode="Markdown")
           #bot.delete_message(message.chat.id, message.message_id)


#    print("DEBUG:")
#    print(message)
#    bot.reply_to(message, 'Debug, entities: ' + str(len(message.entities)))

try:
  bot.polling(none_stop=True)
except Exception as e:
        logger.error(e)
        time.sleep(5)

