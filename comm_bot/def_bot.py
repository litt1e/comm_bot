import telebot
from telebot import types
from comm_bot import models
from comm_bot.bot import bot_action
from comm_bot.bot import config
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

bot = telebot.TeleBot(config.token)


def about_user(message):
    try:
        message = message.message
    except AttributeError:
        message = message
    user = get_user(message)
    return {
        'name': user.name,
        'shortname': user.login,
        'desc': user.description,
        'date': user.date
    }


##########################
#  here's all for /start #
##########################


def get_description(message):
    user = get_user(message)
    user.description(message.text)
    bot_action.set_position(
        user_id=message.chat.id,
        position='nothing'
    )
    a_u = about_user(message)
    info_about = "Имя: %s\nСсылка: %s\nДата начала постинга: %s\nОписание: %s" % (a_u['name'],
                                                                                  a_u['shortname'],
                                                                                  a_u['date'],
                                                                                  a_u['desc'])
    bot.send_message(message.chat.id, info_about)


def no_description(call):
    bot_action.set_position(
        user_id=call.message.chat.id,
        position='nothing'
    )
    a_u = about_user(call.message)
    info_about = "Имя: %s\nСсылка: %s\nДата начала постинга: %s\nОписание: %s" % (a_u['name'],
                                                                                  a_u['shortname'],
                                                                                  a_u['date'],
                                                                                  a_u['desc'])
    bot.send_message(call.message.chat.id, 'ок, без описания\n\n' + info_about)  # и тут тоже)


def get_user(message):
    try:
        user = models.User.objects.get(id=message.chat.id)
    except models.User.DoesNotExist:
        user = bot_action.create_user(
            name=message.chat.first_name,
            login=message.chat.username,
            user_id=message.chat.id
        )
        bot_action.set_position(
            user_id=message.chat.id,
            position='get_description'
        )
        keys = types.InlineKeyboardMarkup()
        keys.add(types.InlineKeyboardButton(text='Мне не нужно описание!!!', callback_data='no_description'))
        bot.send_message(message.chat.id, "Введите описание", reply_markup=keys)
        return user
    else:
        return user


def start(message):
    get_user(message.chat.id)
    bot_action.set_position(
        user_id=message.chat.id,
        position='nothing'
    )


###########################
# here's end of /start   ##
###########################
# and start of /new_post ##
###########################




def get_title(message):
    message_id = bot_action.get_position(message.chat.id).split()[1]
    bot.delete_message(message.chat.id, message_id)
    post = bot_action.create_post(user_id=message.chat.id, title=message.text, text='Пост ещё не создан')
    msg = bot.send_message(message.chat.id, 'Теперь вводите текст')
    bot_action.set_position(user_id=message.chat.id, position='get_text ' + str(msg.message_id) + ' ' + str(post.id))


def no_title(call):
    call.message.text("_")
    get_title(call.message)


def get_text(message):
    message_id = bot_action.get_position(message.chat.id).split()
    bot.delete_message(message.chat.id, message_id[1])
    post = models.Thread.objects.get(id=message_id[2])
    post.text = message.text
    post.save()
    message = "**"+post.title+"**\n\n"+post.text
    key=types.InlineKeyboardMarkup()
    key.add(
        types.InlineKeyboardButton(
            text='Открыть комментарии',
            url='https://josephchekhov.pythonanywhere.com/users/%s/threads/%s/' % (message.chat.username, post.id)
        )
    )
    bot.send_message(message.chat.id, message, reply_markup=key, parse_mode='Markdown')
    bot_action.set_position(user_id=message.chat.id, position='nothing')


def new_post(message):
    try:
        message = message.message
    except AttributeError:
        message = message
    msg = bot.send_message(chat_id=message.chat.id,
                     text='Введите заголовок.',)
    bot_action.set_position(
        user_id=message.chat.id,
        position='get_title ' + str(msg.message_id)
    )
    keys = types.InlineKeyboardMarkup()
    keys.add(types.InlineKeyboardButton(text='Мне не нужен заголовок', callback_data='no_title ' + str(msg.message_id)))
    bot.edit_message_text(text='Введите заголовок', chat_id=message.chat.id, message_id=msg.message_id, reply_markup=keys)


############################
# here's end of /new_post ##
############################
# here's start of /menu   ##
############################


def menu(message):
    msg = bot.send_message(message.chat.id, "Меню")
    keys = types.InlineKeyboardMarkup()
    buttons = {
        "Обо мне": "about_me",
        "Мои посты": "all_my_posts",
        "Самоуничтожение": "self_destruction",
        "Создать пост": "new_post"
    }
    for button in buttons:
        buttons[button] += ' ' + str(msg.message_id)
        keys.add(types.InlineKeyboardButton(text=button, callback_data=buttons[button]))

    bot.edit_message_text(text='Меню', message_id=msg.message_id, chat_id=message.chat.id, reply_markup=keys)


def self_destruction(call):
    keys = types.InlineKeyboardMarkup()
    msg = bot.send_message(call.message.chat.id, "Вы действительно хотите удалить все свои посты?")
    keys.add(types.InlineKeyboardButton(text='Нет', callback_data='no ' + str(msg.message_id)))
    keys.add(types.InlineKeyboardButton(text='Да', callback_data='yes_delete_all_posts ' + str(msg.message_id)))
    bot.edit_message_text(text='Вы действительно хотите удалить все свои посты?',
                          chat_id=call.message.chat.id,
                          message_id=msg.message_id,
                          reply_markup=keys)


def delete_all_posts(call)
    user = get_user(call.message)
    posts = models.Thread.objects.filter(user=user)
    for post in posts:
        post.delete()

    user.description = 'DELETED'
    user.save()
    bot.send_message(call.message.chat.id, 'Все посты удалены')


def no(call):
    bot.send_message(call.message.chat.id, 'Ок, не удаляем посты')
    bot_action.set_position(user_id=call.message.chat.id, position='nothing')
    menu(call.message)


def all_my_posts(call):
    posts = models.Thread.objects.filter(user__id=call.message.chat.id)
    if posts:
        buttons = {}
        keys = types.InlineKeyboardMarkup()
        msg = bot.send_message(call.message.chat.id, 'Ваши посты:')
        for post in posts:
            keys.add(
                types.InlineKeyboardButton(
                    text=post.title, callback_data='post ' + str(msg.message_id) + ' ' + str(post.id)
                )
            )
            keys.add(
                types.InlineKeyboardButton(
                    text='Удалить этот пост', callback_data='delete_post ' + str(msg.message_id) + ' ' + str(post.id)
                )
            )
        keys.add(
            types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu ' + str(msg.message_id))
        )

    else:
        bot.send_message(call.message.chat.id, 'У вас еще нет ни одного поста\n'
                                               'Чтобы создать новый пост нажмите на кнопку в меню')
        menu(call.message)


def post(call):
    post = models.Thread.objects.get(id=call.data.split()[2])
    message = "**" + post.title + "**\n\n" + post.text
    key = types.InlineKeyboardMarkup()
    key.add(
        types.InlineKeyboardButton(
            text='Открыть комментарии',
            url='https://josephchekhov.pythonanywhere.com/users/%s/threads/%s/' % (call.message.chat.username, post.id)
        )
    )
    bot.send_message(message.chat.id, message, reply_markup=key, parse_mode='Markdown')
    bot_action.set_position(user_id=message.chat.id, position='nothing')


def about_me(call):
    message = call.message
    a_u = about_user(message)
    info_about = "Имя: %s\nСсылка: %s\nДата начала постинга: %s\nОписание: %s" % (a_u['name'],
                                                                                  a_u['shortname'],
                                                                                  a_u['date'],
                                                                                  a_u['desc'])
    msg = bot.send_message(message.chat.id, info_about)
    keys = types.InlineKeyboardMarkup()
    keys.add(
        types.InlineKeyboardButton(
            text='Вернуться в меню', callback_data='menu ' + str(msg.message_id)
        )
    )
    bot.edit_message_text(
        text=info_about,
        chat_id=message.chat.id,
        message_id=msg.message_id,
        reply_markup=keys
    )



@csrf_exempt
def webhook(request):
    update = types.Update.de_json(request.body.decode(encoding='utf-8'))
    # update = str(request.body.decode(encoding='utf-8'))
    bot.process_new_updates([update])
    return JsonResponse({"ok": "POST request processed"})


@bot.message_handler(content_types=['text'])
def command_router(message):

    try:
        status = bot_action.get_position(message.chat.id)

    except models.User.DoesNotExist:
        bot_action.create_user(message.chat.first_name, message.chat.username, message.chat.id)
        status = bot_action.get_position(message.chat.id)

    commands = {
        'start': start,
        'new_post': new_post,
        'menu': menu,
    }
    statuses = {
        'nothing': None,
        'get_description': get_description,
        'get_title': get_title,
        'get_text': get_text
    }

    if status in statuses and message.text[1:] not in commands:
        statuses[status.split()[0]](message)

    elif message.text[1:] in commands:
        commands[message.text[1:]](message)


@bot.callback_query_handler(func=lambda call: True)
def call_back(call):
    if call.message:
        bot.delete_message(call.message.chat.id, call.data.split()[1])
        calls = {
            'no_descrition': no_description,
            'no_title': no_title,
            'self_destruction': self_destruction,
            'no': no,
            'yes_delete_all_posts': delete_all_posts,
            'all_my_posts': all_my_posts,
            'post': post
        }
        calls[call.data.split()[0]](call=call)