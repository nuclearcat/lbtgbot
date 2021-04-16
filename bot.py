#!/usr/bin/env python3
#pip3 install PyTelegramBotAPI==3.6.7
#https://github.com/eternnoir/pyTelegramBotAPI
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from threading import Timer
import toml
import json
import hashlib
import time
import logging
import signal
import sys, os

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    os._exit(1)

def mention_string(user):
      user_id = user.id 
      user_name = user.first_name 
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

expiring_welcome = []

with open(r'bot.cfg') as file:
  cfgopt = toml.load(file, _dict=dict)
  print(cfgopt)

logging.basicConfig(filename='bot.log', level=logging.INFO)

bot = telebot.TeleBot(cfgopt["auth"]["token"])
signal.signal(signal.SIGINT, signal_handler)

def confirm_user_welcome(id):
  print("Allowing user")
  for i in expiring_welcome:
    if (i["person"] == id):
      print("Person found")
      bot.delete_message(i["chat"], i["message"].message_id)
      # Remove user from newusers list
      cfgopt["users"]["newmembers"].remove(i["person"])
      # And save
      with open('bot.cfg', 'w') as f:
        toml.dump(cfgopt, f)
      bot.restrict_chat_member(i["chat"], i["person"], can_send_messages=True,
                                         can_send_media_messages=True,
                                         can_send_other_messages=True,
                                         can_add_web_page_previews=True)
      expiring_welcome.remove(i)
      return 1
  return 0

def housekeeping():
  print("Housekeeping ")

  if (len(expiring_welcome) > 0):
    for i in expiring_welcome:
      # Expired
      if (time.time() - i["timestamp"] > 30):
        print("Expired welcome, guest overstay")
        bot.kick_chat_member(i["chat"], i["person"], until_date=time.time()+60)
        bot.delete_message(i["chat"], i["message"].message_id)
        expiring_welcome.remove(i)


  # Restart timer (i know, ugly, i just dont know python alternatives for this)
  t = Timer(5.0, housekeeping)
  t.start()

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Yes", callback_data="cb_yes"),
                               InlineKeyboardButton("No", callback_data="cb_no"))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    rcode = 0
    if call.data == "cb_yes":
        rcode = confirm_user_welcome(call.from_user.id)
    elif call.data == "cb_no":
        rcode = confirm_user_welcome(call.from_user.id)

    print(call)
    if (rcode == 0):
      bot.answer_callback_query(call.id, "This question is expired or not for you")

@bot.message_handler(commands=['start', 'help', 'trustme', 'userid', 'hackme', 'spam', 'nofight', 'id', 'human'])
def commands_handling(message):
#    print(message)
    if(message.chat.type == "private"):
        if (message.text.startswith("/start")):
            bot.reply_to(message, cfgopt["users"]["startmsg"])

        if (message.text.startswith("/id")):
            print("ID request received")
            bot.reply_to(message, cfgopt["misc"]["id"])


#    if (message.text.startswith("/debug")):
#          welcome = {}
#          welcome["message"] = bot.send_message(message.chat.id, cfgopt["lang"]["welcome"], reply_markup=gen_markup())
#          welcome["timestamp"] = time.time()
#          welcome["person"] = message.from_user.id
#          welcome["chat"] = message.chat.id
#          expiring_welcome.append(welcome)
#          bot.delete_message(message.chat.id, message.message_id)



#    if(message.chat.type == "supergroup" and message.text.startswith("/spam")):
#        if (message.from_user.id in cfgopt["users"]["trusted"] and message.reply_to_message is not None):
#            logging.info('ADMIN: User '+str(message.from_user.id)+' marked message "'+message.reply_to_message.text+'" as spam')
#            user_id = message.reply_to_message.from_user.id
#            user_name = message.reply_to_message.from_user.first_name
#            mention = "["+user_name+"](tg://user?id="+str(user_id)+")"
#            bot.reply_to(message.reply_to_message, "Hey," + mention + " ," + cfgopt["lang"]["nospamplease"], parse_mode="Markdown")
#            bot.delete_message(message.reply_to_message.chat.id, message.reply_to_message.message_id)
#            bot.restrict_chat_member(message.reply_to_message.chat.id, message.reply_to_message.from_user.id, until_date=time.time()+ cfgopt["misc"]["spam_mute_duration"])
#        bot.delete_message(message.chat.id, message.message_id)

#    if(message.chat.type == "supergroup" and message.text.startswith("/nofight")):
#        if (message.from_user.id in cfgopt["users"]["trusted"] and message.reply_to_message is not None):
#            if (time.time() - message.reply_to_message.date < cfgopt["misc"]["fightage"]):
#              user_id = message.reply_to_message.from_user.id 
#              user_name = message.reply_to_message.from_user.first_name 
#              mention = "["+user_name+"](tg://user?id="+str(user_id)+")"            
#              bot.reply_to(message.reply_to_message, cfgopt["lang"]["nofight"], parse_mode="Markdown")
#              bot.delete_message(message.reply_to_message.chat.id, message.reply_to_message.message_id)
#              bot.restrict_chat_member(message.reply_to_message.chat.id, message.reply_to_message.from_user.id, until_date=time.time()+ 300)
#        bot.delete_message(message.chat.id, message.message_id)

#    if(message.chat.type == "supergroup" and message.text.startswith("/human")):
#      logging.info('ADMIN: User '+str(message.from_user.id)+' marked person "'+mention_string(message.reply_to_message)+'" as human')
#      cfgopt["users"]["newmembers"].remove(message.reply_to_message.from_user.id)
#      with open('bot.cfg', 'w') as f:
#        toml.dump(cfgopt, f)
#      bot.delete_message(message.chat.id, message.message_id)


# Handling new members
# TODO: Check new member id to estimate age?
@bot.message_handler(content_types=[
    "new_chat_members"
])
def new_chat_member_handling(message):
    # TODO handle multiple members
    #if (len(message.new_chat_members) > 0):
    #  print(message.new_chat_members[0])

    # Check if it is chat admin invited someone
    info = bot.get_chat_administrators(message.chat.id)
    for i in info:
      if (i.user.id == message.from_user.id):
        return

    for x in message.new_chat_members:
      welcome = {}
      welcome["message"] = bot.send_message(message.chat.id, mention_string(x) + "! " + cfgopt["lang"]["welcome"], reply_markup=gen_markup(), parse_mode="Markdown")
      welcome["timestamp"] = time.time()
      welcome["person"] = x.id
      welcome["chat"] = message.chat.id
      expiring_welcome.append(welcome)
      bot.delete_message(message.chat.id, message.message_id)
      bot.restrict_chat_member(message.chat.id, x.id, until_date=time.time()+300)
      cfgopt["users"]["newmembers"].append(x.id)
      with open('bot.cfg', 'w') as f:
        toml.dump(cfgopt, f)

# Handle all messages
@bot.message_handler(func=lambda m: True, content_types=["text", "photo", "video"])
def handle_all(message):
    # debug
    #print(message)

    # Message contain some links
    if (message.from_user.id in cfgopt["users"]["newmembers"] and message.entities != None and len(message.entities) > 0):
      user_id = message.from_user.id 
      user_name = message.from_user.first_name 
      mention = "["+user_name+"](tg://user?id="+str(user_id)+")"

      bot.reply_to(message, cfgopt["lang"]["nolinks"])
      bot.delete_message(message.chat.id, message.message_id)
      bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time()+ 60)

    # This is just initial configuration trigger and verification if bot belongs to his own group
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

    # Fetch admins list (todo: update them?)
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
           # TODO: expire this message
           #bot.delete_message(message.chat.id, message.message_id)

t = Timer(5.0, housekeeping)
t.start()


while(1):
 try:
   bot.polling(none_stop=True)
 except Exception as e:
   #logger.error(e)
   time.sleep(5)
 

