from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button, BotCommand as Command, InputFile as File
from telemod import Listener, TimeOut
from random import randint
from server import server
import asyncio, json, os, telebot, requests

bot_token = Config.TG_BOT_TOKEN
app = AsyncTeleBot(token=bot_token)
loop = asyncio.get_event_loop()
listener = Listener(app, loop)


@app.message_handler(commands=["start"], chat_types="private")
async def start(message: Message):
  user_id = message.from_user.id
  if user_id in banned:
    await app.reply_to(
        message, "- تم حظرك من استخدام البوت تواصل مع المطور ليرفع عنك الحظر.")
    return
  if str(user_id) not in users:
    users[str(user_id)] = {
        "channels": [],
        "settings": {
            "comment_button": False,
            "channel_button": False,
            "add_rights": False,
            "add_emo": False,
        },
        "emo": "👍",
        "rights": f"@{message.from_user.username}"
    }
    write(users_db, users)
    if others.get("options")["new_members_notice"]:
      for admin in admins:
        caption: str = f"-> عضو جديد استخدم البوت 🔥\n\n-> ايدي : {user_id}\n-> يوزر : @{message.from_user. username}\n\n-> عدد الأعضاء الحاليين : {len(users)}"
        try:
          await app.send_message(int(admin), caption)
        except:
          continue
  subscribe = await subscription(user_id)
  if subscribe:
    caption = f"عذرا عزيزي\nعليك الإشتراك بقناة البوت أولا لتتمكن من استخدامه\n{subscribe['channel']}\nاشترك ثم ارسل : /start"
    await app.reply_to(
        message, caption
        if others.get("subscribe") is None else others.get("subscribe"))
    return  # @ELHYBA & @Source_Ze
  name = message.from_user.first_name
  if "message" in message.text:
    data = message.text.split("_", 3)
    chat_id = data[-1]
    message_id = data[1]
    try:
      response = await listener.listen_to(
          message,
          "- أرسل تعليقك الآن.\n- سيتم إلغاء استلام التعليق خلال 30 ثانيه.",
          reply_to_message_id=message.id,
          timeout=30)
    except TimeOut:
      await app.reply_to(message, "تم إلغاء استلام التعليق.")
      return
    await add_comment(response, chat_id, message_id, user_id)
    await app.reply_to(response, "تم ارسال تعليقك.💙")
    return
  markup = Keyboard([[Button("- المطور -", "ELHYBA.t.me")],
                     [
                         Button("- قنواتك -", callback_data="my_channels"),
                         Button("- اضف قناه -",
                                callback_data="users_add_channel"),
                         Button("- حذف قناه -",
                                callback_data="users_remove_channel")
                     ],
                     [
                         Button("- نشر -", callback_data="post"),
                         Button("- إعداداتك -", callback_data="my_settings")
                     ], [
                         Button("- تعليمات البوت -", callback_data="help"),
                     ]])
  caption = f"مرحبًا بك عزيزي {name} في بوت ادارة القنوات.\nاستعمل الأزرار في الأسفل لتتمكن من إضافة قناتك 💙."
  await app.reply_to(
      message,
      caption if others.get("start") is None else others.get("start"),
      reply_markup=markup)


async def add_comment(response, chat_id, message_id, user_id):
  bot = await app.get_me()
  chat_id = int(chat_id) if chat_id.startswith("-") else f"@{chat_id}"
  copied = await app.copy_message(chat_id=chat_id,
                                  from_chat_id=user_id,
                                  message_id=response.id,
                                  reply_to_message_id=message_id)
  markup = Keyboard([[
      Button(
          "- لنشر تعليقك -",
          url=
          f"https://t.me/{bot.username}?start=message_{message_id}_chat_{chat_id if isinstance(chat_id, int) else chat_id.split('@')[-1]}"
      )
  ]])
  caption = (str(response.caption) if any([
      response.animation, response.audio, response.photo, response.video,
      response.video_note, response.voice, response.dice, response.document
  ]) else str(response.text))
  comment_caption = f"{caption}\n\n- [صاحب التعليق](tg://openmessage?user_id={user_id})"
  if "None" in caption: caption = caption.split("None")[-1]
  if any([
      response.animation, response.audio, response.photo, response.video,
      response.video_note, response.voice, response.dice, response.document
  ]):
    try:
      await app.edit_message_caption(
          chat_id=chat_id,
          message_id=copied.message_id,
          caption=comment_caption if isinstance(comment_caption, str) else "_",
          parse_mode="Markdown",
          reply_markup=markup  # @ELHYBA & @Source_Ze
      )
    except telebot.asyncio_helper.ApiTelegramException:
      ...
  else:
    await app.edit_message_text(
        chat_id=chat_id,
        message_id=copied.message_id,
        text=comment_caption if isinstance(comment_caption, str) else "_",
        parse_mode="Markdown",
        reply_markup=markup)


@app.callback_query_handler(func=lambda callback: callback.data == "help")
async def helpness(callback: CallbackQuery):
  user_id = callback.from_user.id
  subscribe = await subscription(user_id)
  if subscribe:
    caption = f"عذرا عزيزي\nعليك الإشتراك بقناة البوت أولا لتتمكن من استخدامه\n{subscribe['channel']}\nاشترك ثم ارسل : /start"
    await app.reply_to(
        callback.message, caption
        if others.get("subscribe") is None else others.get("subscribe"))
    return  # @ELHYBA & @Source_Ze
  name = callback.from_user.full_name
  caption = f"""
- مرحبا عزيزي {name}.

- عليك اولا رفع البوت ادمن في قناتك

- يمكنك اضافة ايموجي تحت المنشور أو ازالته.
- يمكنك اضافة أو ازالة حقوق القناه والناشر.
- يمكنك إضافة زر ب اسم + رابط القناه.
- يمكنك اضافة زر التعليقات.
"""
  markup = Keyboard([[Button("- العوده -", callback_data="users_start")]])
  await app.edit_message_text(chat_id=user_id,
                              message_id=callback.message.id,
                              text=caption,
                              reply_markup=markup)


@app.callback_query_handler(
    func=lambda callback: callback.data == "users_start")
async def restart(callback: CallbackQuery):
  name = callback.from_user.full_name
  user_id = callback.from_user.id
  subscribe = await subscription(user_id)
  if subscribe:
    caption = f"عذرا عزيزي\nعليك الإشتراك بقناة البوت أولا لتتمكن من استخدامه\n{subscribe['channel']}\nاشترك ثم ارسل : /start"
    await app.reply_to(
        callback.message, caption
        if others.get("subscribe") is None else others.get("subscribe"))
    return  # @ELHYBA & @Source_Ze
  markup = Keyboard([[Button("- المطور -", "ELHYBA.t.me")],
                     [
                         Button("- قنواتك -", callback_data="my_channels"),
                         Button("- اضف قناه -",
                                callback_data="users_add_channel"),
                         Button("- حذف قناه -",
                                callback_data="users_remove_channel")
                     ],
                     [
                         Button("- نشر -", callback_data="post"),
                         Button("- إعداداتك -", callback_data="my_settings")
                     ], [
                         Button("- تعليمات البوت -", callback_data="help"),
                     ]])
  caption = f"مرحبًا بك عزيزي {name} في بوت ادارة القنوات.\nاستعمل الأزرار في الأسفل لتتمكن من إضافة قناتك 💙."
  await app.edit_message_text(
      chat_id=callback.message.chat.id,
      message_id=callback.message.id,
      text=caption if others.get("start") is None else others.get("start"),
      reply_markup=markup)


@app.callback_query_handler(
    func=lambda callback: callback.data == "my_channels")
async def my_channels(callback: CallbackQuery):
  user_id = callback.from_user.id
  subscribe = await subscription(user_id)
  if subscribe:
    caption = f"عذرا عزيزي\nعليك الإشتراك بقناة البوت أولا لتتمكن من استخدامه\n{subscribe['channel']}\nاشترك ثم ارسل : /start"
    await app.reply_to(
        callback.message, caption
        if others.get("subscribe") is None else others.get("subscribe"))
    return  # @ELHYBA & @Source_Ze
  user_channels = users[str(user_id)]["channels"]
  if len(user_channels) == 0:
    await app.answer_callback_query(callback.id,
                                    "ليس لديك أي قنوات مضافه بعد.",
                                    show_alert=True)
    return
  markup = []  # @ELHYBA & @Source_Ze
  for username in user_channels:
    channel = await app.get_chat(username)
    name = channel.title
    typeness = channel.type
    url = (await app.create_chat_invite_link(username)).invite_link if type(
        username) == type(1) else f"{username.split('@')[-1]}.t.me"
    name_btn = [Button(name, url)]
    info_btn = [
        Button(username, callback_data="username"),
        Button(typeness, callback_data="typeness")
    ]
    markup.append(name_btn)
    markup.append(info_btn)
  markup.append([Button("- العوده -", callback_data="users_start")])
  caption = "- هذه هي قنواتك الحاليه: "
  await app.edit_message_text(
      chat_id=user_id,
      message_id=callback.message.id,
      text=caption,  # @ELHYBA & @Source_Ze
      reply_markup=Keyboard(markup))


@app.callback_query_handler(
    func=lambda callback: callback.data == "users_add_channel")
async def users_add_channel(callback: CallbackQuery):
  user_id = callback.from_user.id
  subscribe = await subscription(user_id)
  if subscribe:
    caption = f"عذرا عزيزي\nعليك الإشتراك بقناة البوت أولا لتتمكن من استخدامه\n{subscribe['channel']}\nاشترك ثم ارسل : /start"
    await app.reply_to(
        callback.message, caption
        if others.get("subscribe") is None else others.get("subscribe"))
    return  # @ELHYBA & @Source_Ze
  user_channels = users[str(user_id)]["channels"]
  if len(user_channels) >= 3:
    await app.answer_callback_query(callback.id,
                                    "لقد وصلت إلى الحد الأقصى من القنوات (3).",
                                    show_alert=True)
    return
  try:
    response = await listener.listen_to(
        callback,
        "- قم بإرسال معرف القناه مبدوءًا ب @ اذا كانت القناه عامه.\n- أو قم  بإعادة توجيه منشور من القناه اذا كانت خاصه.\n- سيتم إلغاء استلام القناه تلقائيا بعد 30 ثانبه.",
        timeout=30)
  except TimeOut:
    await app.send_message(chat_id=user_id, text="انتهى وقت استلام القناه.")
    return
  await app.delete_message(user_id, response.id)
  if response.forward_from_chat:
    channel = response.forward_from_chat.id
  else:
    channel = response.text
  if channel is str:  # @ELHYBA & @Source_Ze
    try:
      await app.get_chat(channel)
    except telebot.asyncio_helper.ApiTelegramException:
      await app.edit_message_text(chat_id=user_id,
                                  message_id=response.output.id,
                                  text="لم يتم إيجاد هذه القناه.")
      return
  try:
    await app.get_chat_administrators(channel)
  except telebot.asyncio_helper.ApiTelegramException:
    await app.edit_message_text(
        chat_id=user_id,
        message_id=response.output.id,
        text="قم برفع البوت ادمن في قناتك أولا ثم اعد إضافة القناه.")
    return
  if channel in users[str(user_id)]["channels"]:
    await app.edit_message_text(chat_id=user_id,
                                message_id=response.output.id,
                                text="هذه القناه مضافه بالفعل.")
    return
  users[str(user_id)]["channels"].append(channel)
  users_channels[str(channel)] = {
      "settings": users[str(user_id)]["settings"],
      "rights": users[str(user_id)]["rights"],
      "emo": users[str(user_id)]["emo"]
  }
  write(users_db, users)
  write(users_channels_db, users_channels)
  await app.edit_message_text(chat_id=user_id,
                              message_id=response.output.id,
                              text="تم إضافة القناه.")


@app.callback_query_handler(
    func=lambda callback: callback.data == "users_remove_channel")
async def users_remove_channel(callback: CallbackQuery):
  user_id = callback.from_user.id
  subscribe = await subscription(user_id)
  if subscribe:
    caption = f"عذرا عزيزي\nعليك الإشتراك بقناة البوت أولا لتتمكن من استخدامه\n{subscribe['channel']}\nاشترك ثم ارسل : /start"
    await app.reply_to(
        callback.message, caption
        if others.get("subscribe") is None else others.get("subscribe"))
    return  # @ELHYBA & @Source_Ze
  user_channels = users[str(user_id)]["channels"]
  if len(user_channels) == 0:
    await app.answer_callback_query(callback.id,
                                    "ليس لديك أي قنوات مضافه بعد.",
                                    show_alert=True)
    return
  markup = []
  for username in user_channels:
    channel = await app.get_chat(username)
    name = channel.title
    name_btn = [Button(name, callback_data=f"remove_user_{username}")]
    markup.append(name_btn)
  markup.append([Button("- العوده -", callback_data="users_start")])
  caption = "- اختر قناه ليتم حذفها: "
  await app.edit_message_text(chat_id=user_id,
                              message_id=callback.message.id,
                              text=caption,
                              reply_markup=Keyboard(markup))


@app.callback_query_handler(
    func=lambda callback: callback.data.startswith("remove_user"))
async def removing_user_channel(callback: CallbackQuery):
  user_id = callback.from_user.id
  channel = callback.data.split("_", 2)[-1]
  users[str(user_id)]["channels"].remove(
      int(channel) if channel.startswith("-") else channel)
  del users_channels[channel]
  write(users_channels_db, users_channels)
  write(users_db, users)
  await app.edit_message_text(chat_id=user_id,
                              message_id=callback.message.id,
                              text="تم حذف القناه موديجاح.",
                              reply_markup=Keyboard([[
                                  Button("- العوده -",
                                         callback_data="users_start")
                              ]]))


@app.callback_query_handler(
    func=lambda callback: callback.data == "my_settings")
async def settings(callback: CallbackQuery):
  user_id = callback.from_user.id
  subscribe = await subscription(user_id)
  if subscribe:
    caption = f"عذرا عزيزي\nعليك الإشتراك بقناة البوت أولا لتتمكن من استخدامه\n{subscribe['channel']}\nاشترك ثم ارسل : /start"
    await app.reply_to(
        callback.message, caption
        if others.get("subscribe") is None else others.get("subscribe"))
    return  # @ELHYBA & @Source_Ze
  user_channels = users[str(user_id)]["channels"]
  if len(user_channels) == 0:
    await app.answer_callback_query(callback.id,
                                    "ليس لديك أي قنوات مضافه بعد.",
                                    show_alert=True)
    return
  markup = channels_markup(user_id)
  caption = "- علامة ❌️ تعني أن الميزه غير مفعله.\n- وعلامة ✅️ تعني أن الميزه مفعله.\n- يمكنك التحكم في كل ميزه حسب احتياجك."
  await app.edit_message_text(chat_id=user_id,
                              message_id=callback.message.id,
                              text=caption,
                              reply_markup=markup)


@app.callback_query_handler(func=lambda callback: callback.data in users[str(
    callback.from_user.id)]["settings"])
async def change_attr(callback: CallbackQuery):
  user_id = callback.from_user.id
  data = callback.data
  users[str(user_id)]["settings"][data] = True if not users[str(
      user_id)]["settings"][data] else False
  user_channels = users[str(user_id)]["channels"]
  try:
    for channel in user_channels:
      users_channels[str(
          channel)]["settings"][data] = True if not users_channels[str(
              channel)]["settings"][data] else False
  except:
    pass
  write(users_channels_db, users_channels)
  write(users_db, users)
  await app.edit_message_reply_markup(chat_id=user_id,
                                      message_id=callback.message.id,
                                      reply_markup=channels_markup(user_id))


@app.callback_query_handler(
    func=lambda callback: callback.data in ["change_emo", "change_rights"])
async def change_emo(callback: CallbackQuery):
  user_id = callback.from_user.id
  data = callback.data
  current = users[str(user_id)]["emo" if data == "change_emo" else "rights"]
  try:
    response = await listener.listen_to(
        callback,
        f"- الحالي : \n{current}\nأرسل {'الإيموجي' if data == 'change_emo' else 'الحقوق'} الجديده.\n- سيتم إلغاء الإستلام بعد 30 ثانيه.",
        timeout=30)
  except TimeOut:
    await app.send_message(chat_id=user_id, text="تم الإلغاء.")
    return
  await app.delete_message(user_id, response.id)
  if response.text == current:
    await app.edit_message_text(
        chat_id=user_id,
        message_id=response.output.id,
        text=
        f"{'الإيموجي' if data == 'change_emo' else 'الحقوق'} الذي أرسلته مضاف بالفعل."
    )
    return
  users[str(user_id)]["emo" if data ==
                      "change_emo" else "rights"] = response.text
  user_channels = users[str(user_id)]["channels"]
  for channel in user_channels:
    users_channels[str(channel)]["emo" if data ==
                                 "change_emo" else "rights"] = response.text
  write(users_db, users)
  write(users_channels_db, users_channels)
  await app.edit_message_text(
      chat_id=user_id,
      message_id=response.output.id,
      text=f"تم تغيير {'الإيموجي' if data == 'change_emo' else 'الحقوق'}.")


@app.callback_query_handler(func=lambda callback: callback.data == "post")
async def post(callback: CallbackQuery):
  user_id = callback.from_user.id
  subscribe = await subscription(user_id)
  if subscribe:
    caption = f"عذرا عزيزي\nعليك الإشتراك بقناة البوت أولا لتتمكن من استخدامه\n{subscribe['channel']}\nاشترك ثم ارسل : /start"
    await app.reply_to(
        callback.message, caption
        if others.get("subscribe") is None else others.get("subscribe"))
    return  # @ELHYBA & @Source_Ze
  user_channels = users[str(user_id)]["channels"]
  if len(user_channels) == 0:
    await app.answer_callback_query(callback.id,
                                    "ليس لديك أي قنوات مضافه بعد.",
                                    show_alert=True)
    return
  markup = [
      [Button("نوع الرساله : ", callback_data="button")],
      [
          Button("- Markdown -", callback_data="change_message_markdown"),
          Button("- HTML -", callback_data="change_message_html"),
          Button("- عاديه -", callback_data="change_message_normal")
      ],
      [  # @ELHYBA & @Source_Ze
          Button("الإرسال إلى : ", callback_data="button")
      ],
  ]
  channels_keys = []
  user_channels = users[str(user_id)]["channels"]
  for username in user_channels:
    channel = await app.get_chat(username)
    name = channel.title
    channels_keys.append(Button(name, callback_data=f"send_to_{username}"))
  markup.append([Button("- الكل -", callback_data="send_to_all")])
  markup.append(channels_keys)
  markup.append([Button("- إرسال الرساله -", callback_data="send_message")])
  markup.append([Button("- العوده -", callback_data="users_start")])
  caption = "- قم بتحديد نوع الرساله وإلى أي قناه سيتم إرسالها."
  await app.edit_message_text(chat_id=user_id,
                              message_id=callback.message.id,
                              text=caption,
                              reply_markup=Keyboard(markup))


@app.callback_query_handler(
    func=lambda callback: callback.data.startswith("change_message"))
async def change_message(callback: CallbackQuery):
  user_id = callback.from_user.id
  data = callback.data.split("_")[-1]
  markup = callback.message.reply_markup.keyboard
  markup[0][0].text = f"نوع الرساله : {data.upper()}"
  markup[0][0].callback_data = data
  await app.edit_message_reply_markup(chat_id=user_id,
                                      message_id=callback.message.id,
                                      reply_markup=Keyboard(markup))


@app.callback_query_handler(
    func=lambda callback: callback.data.startswith("send_to"))
async def send_to(callback: CallbackQuery):
  user_id = callback.from_user.id
  data = callback.data.split("_", 2)[-1]
  markup = callback.message.reply_markup.keyboard
  if data != "all":
    channel = await app.get_chat(data if data.startswith("@") else int(data))
    markup[2][0].text = f"الإرسال إلى : {channel.title}"
  else:
    markup[2][0].text = "الإرسال إلى : ALL"
  markup[2][0].callback_data = data
  await app.edit_message_reply_markup(chat_id=user_id,
                                      message_id=callback.message.id,
                                      reply_markup=Keyboard(markup))


@app.callback_query_handler(
    func=lambda callback: callback.data == "send_message")
async def send_message(callback: CallbackQuery):
  user_id = callback.from_user.id
  markup = callback.message.reply_markup.keyboard  # @ELHYBA & @Source_Ze
  message_type = markup[0][0].callback_data
  to_chat = markup[2][0].callback_data
  await app.delete_message(user_id, callback.message.id)
  try:
    response = await listener.listen_to(
        callback,
        text=
        "- قم بإرسال الرساله الآن.\n- سيتم إلغاء الأرسال تلقائيا بعد 30 ثانيه.",
        timeout=30)
  except TimeOut:
    await app.send_message(user_id,
                           "- تم إلغاء ارسال رساله.",
                           reply_markup=Keyboard([[
                               Button("- العوده -",
                                      callback_data="users_start")
                           ]]))
    return
  user_channels = users[str(user_id)]["channels"]
  if to_chat == "all":
    for channel in user_channels:
      copied = await app.copy_message(
          from_chat_id=user_id,
          chat_id=channel,
          message_id=response.id,
          parse_mode="HTML" if message_type != "markdown" else "Markdown")
      await editor(response, channel, copied.message_id, user_id)
  else:
    chat_id = to_chat if to_chat.startswith("@") else int(to_chat)
    copied = await app.copy_message(
        chat_id=chat_id,
        from_chat_id=user_id,
        message_id=response.id,
        parse_mode="HTML" if message_type != "markdown" else "Markdown",
        disable_notification=True)
    await editor(response, chat_id, copied.message_id, user_id)
  await app.reply_to(response,
                     "- تم أرسال الرساله موديجاح.💙",
                     reply_markup=Keyboard(
                         [[Button("- العوده -",
                                  callback_data="users_start")]]))


async def editor(response, chat_id, message_id, user_id=False):
  user_rights = users[str(user_id)]["rights"] if user_id else users_channels[
      str(chat_id)]["rights"]
  user_emo = users[str(user_id)]["emo"] if user_id else users_channels[str(
      chat_id)]["emo"]
  user_settings = users[str(
      user_id)]["settings"] if user_id else users_channels[str(
          chat_id)]["settings"]
  if user_settings["add_rights"]:
    caption = (str(response.caption) if any([
        response.animation, response.audio, response.photo, response.video,
        response.video_note, response.voice, response.dice, response.document
    ]) else str(response.text)) + "\n" + user_rights
    if "None" in caption: caption = caption.split("None")[-1]
    if any([
        response.animation, response.audio, response.photo, response.video,
        response.video_note, response.voice, response.dice, response.document
    ]):
      try:
        await app.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=caption if isinstance(caption, str) else "_",
            parse_mode="HTML")
      except telebot.asyncio_helper.ApiTelegramException:
        ...
    else:
      await app.edit_message_text(
          chat_id=chat_id,
          message_id=message_id,
          text=caption if isinstance(caption, str) else "_",
          parse_mode="HTML")
  if user_settings["add_emo"]:
    if votes.get(str(chat_id)) is None: votes[str(chat_id)] = {}
    vote_id = randint(0, 975785)
    while str(vote_id) in votes[str(chat_id)]:
      vote_id = randint(0, 975785)
    votes[str(chat_id)][str(vote_id)] = []
    write(votes_db, votes)
    markup = Keyboard([[Button(user_emo, callback_data=f"vote_0_{vote_id}")]])
    await app.edit_message_reply_markup(chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=markup)
  if user_settings["channel_button"]:
    channel_title = (await app.get_chat(chat_id)).title
    if user_settings["add_emo"]:
      markup = Keyboard([[
          Button(user_emo, callback_data=f"vote_0_{vote_id}"),
          Button(channel_title,
                 url=f"{chat_id.split('@')[-1]}.t.me" if isinstance(
                     chat_id, str) else
                 (await app.create_chat_invite_link(chat_id)).invite_link)
      ]])
    else:
      markup = Keyboard([[
          Button(channel_title,
                 url=f"{chat_id.split('@')[-1]}.t.me" if isinstance(
                     chat_id, str) else
                 (await app.create_chat_invite_link(chat_id)).invite_link)
      ]])
    await app.edit_message_reply_markup(
        chat_id=chat_id,  # @ELHYBA & @Source_Ze
        message_id=message_id,
        reply_markup=markup)
  if user_settings["comment_button"]:
    bot = await app.get_me()
    if all([user_settings["add_emo"], user_settings["channel_button"]]):
      markup = Keyboard([
          [
              Button(user_emo, callback_data=f"vote_0_{vote_id}"),
              Button(channel_title,
                     url=f"{chat_id.split('@')[-1]}.t.me" if isinstance(
                         chat_id, str) else
                     (await app.create_chat_invite_link(chat_id)).invite_link)
          ],
          [
              Button(
                  "اضف تعليق ♡.",
                  url=
                  f"https://t.me/{bot.username}?start=message_{message_id}_chat_{chat_id if isinstance(chat_id, int) else chat_id.split('@')[-1]}"
              )
          ]
      ])
    elif user_settings["add_emo"]:
      markup = Keyboard([[
          Button(user_emo, callback_data=f"vote_0_{vote_id}"),
          Button(
              "اضف تعليق ♡.",
              url=
              f"https://t.me/{bot.username}?start=message_{message_id}_chat_{chat_id if isinstance(chat_id, int) else chat_id.split('@')[-1]}"
          )
      ]])
    elif user_settings["channel_button"]:
      markup = Keyboard([[
          Button(channel_title,
                 url=f"{chat_id.split('@')[-1]}.t.me" if isinstance(
                     chat_id, str) else
                 (await app.create_chat_invite_link(chat_id)).invite_link),
          Button(
              "اضف تعليق ♡.",
              url=
              f"https://t.me/{bot.username}?start=message_{message_id}_chat_{chat_id if isinstance(chat_id, int) else chat_id.split('@')[-1]}"
          )
      ]])
    await app.edit_message_reply_markup(chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=markup)


@app.message_handler(regexp=r"^(المطور|المبرمج|مودي)$")
async def dev(message: Message):
  chat_id = 6581896306
  user = await app.get_chat(chat_id)
  user_bio = user.bio
  nickname = user.first_name
  username = user.username
  photo_path = "developer.jpg"
  file_id = user.photo.big_file_id
  file_info = await app.get_file(file_id)
  file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_info.file_path}"
  response = requests.get(file_url)
  with open(photo_path, "wb") as f:
    f.write(response.content)
  caption = user_bio
  markup = Keyboard([[Button(nickname, url=f"{username}.t.me")]
                     ])  # @ELHYBA & @Source_Ze
  await app.send_photo(chat_id=message.chat.id,
                       photo=File(file=photo_path),
                       caption=caption,
                       reply_markup=markup)


@app.callback_query_handler(
    func=lambda callback: callback.data.startswith("vote"))
async def vote(callback: CallbackQuery):
  data = callback.data
  chat_id = callback.message.chat.id
  channel_user = callback.message.chat.username
  user_id = callback.from_user.id
  info = data.split("_")[1:]
  try:
    if (await app.get_chat_member("@" + channel_user, user_id)).status not in [
        "member", "creator", "administrator"
    ]:
      await app.answer_callback_query(
          callback.id,
          "يجب عليك الإنضمام أولًا لتتمكن من التصويت.🚫",
          show_alert=True)
      return
  except:
    ...
  if user_id in votes[
      str(chat_id) if channel_user is None else f"@{channel_user}"][info[-1]]:
    await app.answer_callback_query(callback.id,
                                    "لقد قمت بالتصويت من قبل.🚫",
                                    show_alert=True)
    return
  votes[str(chat_id) if channel_user is None else f"@{channel_user}"][
      info[-1]].append(user_id)
  write(votes_db, votes)
  markup = callback.message.reply_markup.keyboard
  emo = markup[0][0].text.split()[-1]
  await app.answer_callback_query(callback.id, f"You reacted to this {emo}")
  text = f"{int(info[0]) +1} {emo}"  # @ELHYBA & @Source_Ze
  markup[0][0].text = text
  markup[0][0].callback_data = f"vote_{int(info[0]) +1}_{info[-1]}"
  await app.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=callback.message.id,
                                      reply_markup=Keyboard(markup))


@app.channel_post_handler(content_types=[
    "text", "photo", "animation", "video", "sticker", "document", "dice",
    "video_note", "audio", "voice"
])
async def channel_post_handler(message: Message):
  chat_id = message.chat.id
  username = message.chat.username
  if str(chat_id) in users_channels:
    channel = chat_id
    await editor(message, channel, message.id)
  elif f"@{username}" in users_channels:
    channel = f"@{username}"
    await editor(message, channel, message.id)
  return


def channels_markup(user_id):
    markup = Keyboard([
        [
            Button(
                "- زر رابط القناه ✅️ -" if users[str(user_id)]["settings"]["channel_button"] else "- زر رابط القناه ❌️ -", 
                callback_data="channel_button"),
        ],
        [
            Button("- تغيير الإيموجي -", callback_data="change_emo"),
            Button(
                "- إضافة ايموجي ✅️ -" if users[str(user_id)]["settings"]["add_emo"] else "- إضافة ايموجي ❌️ -", 
                callback_data="add_emo"),
        ],
        [
            Button("- تغيير الحقوق -", callback_data="change_rights"),
            Button(
                "- إضافة حقوق ✅️ -" if users[str(user_id)]["settings"]["add_rights"] else "- إضافة حقوق ❌️ -", 
                callback_data="add_rights"),
        ],
        [
            Button(
                "- زر التعليقات ✅️ -" if users[str(user_id)]["settings"]["comment_button"] else "- زر التعليقات ❌️ -", 
                callback_data="comment_button"),
        ],# @ELHYBA & @Source_Ze
        [
            Button("- العوده -", callback_data="users_start")
        ]
    ])
    return markup


@app.message_handler(commands=["admin"], chat_types="private")
async def admin(message: Message):
  user_id = message.from_user.id
  if user_id not in admins:
    await app.reply_to(message, text="هذا الأمر يخص المشرفين")
    await dev(message)
    return  # @ELHYBA & @Source_Ze
  markup = Keyboard(keyboard())
  info = await app.get_chat(user_id)
  admin_name = info.first_name
  caption = f"-> مرحبا عزيزي الأدمن ( `{admin_name}` )\n\n-> احصائيات: \n-> الأعضاء : {len(users)}\n-> المحظورين : {len(banned)}\n\n-> أوامر أخرى : \n- حظر + الأيدي\n- رفع حظر + الأيدي\n- رفع ادمن + الأيدي\n- تنزيل ادمن + الأيدي"
  await app.reply_to(message, text=caption, reply_markup=markup)
  # @ELHYBA & @Source_Ze


@app.message_handler(regexp=r"^(حظر)", chat_types=["private"])
async def ban(message: Message):
  user_id = message.from_user.id
  if user_id not in admins:
    await app.reply_to(message, text="هذا الأمر يخص المشرفين")
    return
  member = message.text.split()[-1]
  if int(member) in admins:
    await app.reply_to(message, text="لا يمكنك حظر هذا المستخدم.")
    return
  if int(member) in banned:
    await app.reply_to(message, text="تم حظر هذا المستخدم من قبل.")
    return
  banned.append(int(member))
  write(banned_db, banned)
  await app.reply_to(message, text="تم حظر هذا المستخدم")
  # @ELHYBA & @Source_Ze


@app.message_handler(regexp=r"^(رفع حظر)", chat_types=["private"])
async def unban(message: Message):
  user_id = message.from_user.id
  if user_id not in admins:
    await app.reply_to(message, text="هذا الأمر يخص المشرفين")
    return
  member = message.text.split()[-1]
  if int(member) in banned:
    banned.remove(int(member))
    write(banned_db, banned)
    await app.reply_to(message, text="تم رفع الحظر عن هذا المستخدم.")
    return  # @ELHYBA & @Source_Ze
  await app.reply_to(message, text="لم يتم حظر هذا المستخدم من قبل.")


@app.message_handler(regexp=r"^(رفع ادمن)", chat_types=["private"])
async def promote(message: Message):
  user_id = message.from_user.id
  if user_id not in admins:
    await app.reply_to(message, text="هذا الأمر يخص المشرفين")
    return
  member = message.text.split()[-1]
  if int(member) in admins:
    await app.reply_to(message, text="هذا المستخدم مشرف بالفعل.")
    return
  if int(member) in banned:
    await app.reply_to(
        message,
        text="هذا المستخدم تم حظره من قبل يرجى رفع الحظر ثم إعادة المحاوله.")
    return
  admins.append(int(member))
  write(admins_db, admins)
  await app.reply_to(message, text="تم ترقية المستخدم لرتبة مشرف")


@app.message_handler(regexp=r"^(تنزيل ادمن)", chat_types=["private"])
async def demote(message: Message):
  user_id = message.from_user.id
  if user_id not in admins:
    await app.reply_to(message, text="هذا الأمر يخص المشرفين")
    return
  member = message.text.split()[-1]
  if int(member) in admins:
    admins.remove(int(member))
    write(admins_db, admins)
    await app.reply_to(message,
                       text="تم تنزيل هذا المستخدم من قائمة المشرفين.")
    return
  await app.reply_to(message, text="هذا المستخدم ليس من المشرفين.")


@app.callback_query_handler(func=lambda callback: callback.data in
                            ["forward_from_users", "new_members_notice"])
async def redefine(callback: CallbackQuery):
  data = callback.data
  others["options"][data] = True if not others["options"][data] else False
  write(others_db, others)
  await app.edit_message_reply_markup(
      chat_id=callback.message.chat.id,
      message_id=callback.message.id,  # @ELHYBA & @Source_Ze
      reply_markup=Keyboard(keyboard()))


@app.callback_query_handler(
    func=lambda callback: callback.data == "add_channel")
async def add_channel(callback: CallbackQuery):
  message = await listener.listen_to(m=callback,
                                     text="أرسل معرف القناه مع مبدوء ب @")
  channel = message.text
  try:
    await app.get_chat(channel)
  except:
    await app.reply_to(message, "لم يتم إيجاد هذه الدردشه.")
    return
  if channel in channels:
    await app.reply_to(message, "القناه موجوده بالفعل.")
    return
  channels.append(channel)
  write(channels_db, channels)
  await app.reply_to(message, "تمت إضافة القناه.")


@app.callback_query_handler(
    func=lambda callback: callback.data == "remove_channel")
async def remove_channel(callback: CallbackQuery):
  message = await listener.listen_to(m=callback,
                                     text="أرسل معرف القناه مع مبدوء ب @")
  channel = message.text
  if channel not in channels:
    await app.reply_to(message, "لم يتم إيجاد هذه الدردشه.")
    return
  channels.remove(channel)
  write(channels_db, channels)
  await app.reply_to(message, "تم حذف القناه.")


@app.callback_query_handler(
    func=lambda callback: callback.data == "current_channels")
async def current_channels(callback: CallbackQuery):
  caption = "- القنوات الحاليه :\n"
  text = "\n".join(channels)
  caption += text
  await app.answer_callback_query(callback_query_id=callback.id,
                                  text=caption,
                                  show_alert=True)


@app.callback_query_handler(
    func=lambda callback: callback.data == "send_storage")
async def send_storage(callback: CallbackQuery):
  files_path = "database"
  files = os.listdir(files_path)
  for file in files:
    file_path = os.path.join(files_path, file)
    await app.send_document(callback.message.chat.id,
                            document=File(file_path))  # @ELHYBA & @Source_Ze


def write(fp, data):
  with open(fp, "w") as file:
    json.dump(data, file, indent=2)


def read(fp):
  if not os.path.exists(fp):
    with open(fp, "w") as file:
      json.dump({} if fp
                not in ["channels.json", "banned.json", "admins.json"] else [],
                file,
                indent=2)
  with open(fp) as file:
    data = json.load(file)
  return data


async def subscription(user_id):
  if len(channels) == 0:
    return False
  status = ["creator", "administrator", "member"]
  for channel in channels:
    member = await app.get_chat_member(chat_id=channel, user_id=user_id)
    if member.status not in status:
      return {
          "channel": channel,
      }
    return False


def keyboard():
  keys = [
      [
          Button(  # @ELHYBA & @Source_Ze
              "- التوجيه من الأعضاء ✅️ -"
              if others.get("options")["forward_from_users"] else
              "- التوجيه من الأعضاء ❌️ -",
              callback_data="forward_from_users"),  # DONE
          Button("- تنبيه الأعضاء الجدد ✅️ -"
                 if others.get("options")["new_members_notice"] else
                 "- تنبيه الأعضاء الجدد ❌️ -",
                 callback_data="new_members_notice")  # DONE
      ],
      [
          Button("- إضافة قناه -", callback_data="add_channel"),  # DONE
          Button("- القنوات الحاليه -",
                 callback_data="current_channels"),  # DONE
          Button("- حذف قناه -", callback_data="remove_channel")  # DONE
      ],
      [
          Button("- التخزين -", callback_data="send_storage")  # DONE
      ]
  ]
  return keys


users_db = "users.json"
channels_db = "channels.json"  # @ELHYBA & @Source_Ze
banned_db = "banned.json"
admins_db = "admins.json"
others_db = "others.json"
votes_db = "votes.json"
users_channels_db = "users_channels.json"
if not os.path.exists(others_db):
  write(others_db,
        {"options": {
            "forward_from_users": True,
            "new_members_notice": True
        }})
users = read(users_db)
admins = read(admins_db)
channels = read(channels_db)
banned = read(banned_db)
others = read(others_db)
votes = read(votes_db)
users_channels = read(users_channels_db)


async def main():
  server()
  commands = [
      Command(command="start", description="Start the bot."),
      Command(command="admin", description="Just for admins.")
  ]
  await app.set_my_commands(commands=commands)
  print((await app.get_me()).full_name)
  await app.infinity_polling()


if __name__ == "__main__":
  loop.run_until_complete(main())

# 〞𝗪𝗥𝗜𝗧𝗧𝗘𝗡 𝗕𝗬 : @ELHYBA
# 〞𝗦𝗢𝗨𝗥𝗖𝗘 : @Source_Ze
