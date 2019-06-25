from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from telebot.types import InlineKeyboardButton

from comm_bot import models
from comm_bot import forms
import telebot

# Create your views here.
# TODO: ~/users/<user_id>/ - here some about user and all his titles
#       ~/users/<user_id>/threads/<thread_id>/ - some title
#       create table in db "users", connect with this one table "thread"


def users(request, login):
    try:
        user = models.User.objects.get(login=login)

    except models.User.DoesNotExist:
        return render_to_response("no_user.html", locals())

    else:

        threads = models.Thread.objects.filter(user=user)
        return render_to_response("users.html", locals())


def save_reply(request, thread_id):
    if request.method == 'POST':
        form = forms.Reply(request.POST)

        if form.is_valid():
            user = request.user
            text = form.cleaned_data['text']
            tr = models.Thread.objects.filter(id=int(thread_id))[0]  # thread
            models.Answer.objects.create(text=text, thread=tr, user=user)


def to_answer(request):
    """!!1!!! сюда передовать только POST !!11!!"""
    form = forms.Answer(request.POST)
    if form.is_valid():
        user = request.user
        text = form.cleaned_data['text']
        answer_to = form.cleaned_data['answer_to']
        answer = models.Answer.objects.create(user=user, text=text, answer_to=answer_to if answer_to else 0)
        if answer.answer_to:
            models.Answer.make_answer(answer)


@csrf_exempt
def thread(request, login, thread_id, reply_form=forms.Reply):
    if request.method == 'POST':
        print(request.POST)
        save_reply(request, thread_id)
    # TODO: сделать шоб у ответов в каждом треде были свои ай ди(начинались с единички везде а то ща везде продолжается типо тред сделали а таам дос хх пор 100 ид ахыхыгыыгыгы
    path = request.get_full_path()

    if 'reply' not in path:
        path += '/reply'
    else:
        answer = False
        redirect(path.replace('reply', ''))

    if not thread_id.isdigit():
        return HttpResponse('404 error<br/>Page not found')

    else:
        thread = models.Thread.objects.get(id=int(thread_id))  # тред энивей 1 будет # спасибо за подказку епта
        answers = models.Answer.objects.filter(thread__id=int(thread_id))
        result = []  # TODO: придумать норм название
        for answer in answers:
            result.append(
                {
                    'user': answer.user,
                    'text': answer.text,
                    'date': answer.date.strftime('%d/%m/%y %a %X'),
                    'id': answer.id
                }
            )

        return render_to_response('thread.html', {'answers': result,
                                                  'thread': thread,
                                                  'answer': lambda answer: answer if answer else '',
                                                  'form': reply_form,
                                                  'path': path,
                                                  'user': request.user})

# # # !!! отсюда начинается всё что надо боту !!! # # #


from comm_bot.bot import config
from comm_bot.bot import bot_action
from telebot import types


bot = telebot.TeleBot(config.token)


def start(message):
    bot_action.create_user(name=message.chat.first_name,
                           login=message.chat.username,
                           user_id=message.chat.id,
                           description=message.text) if message.text else bot_action.create_user(name=message.chat.name,
                                                                                                 login=message.chat.username,
                                                                                                 user_id=message.chat.id)


def make_post(message, title):
    bot_action.create_post(user_id=message.chat.id,
                           title=title,
                           text=message.text)


def new_post(message):
    bot_action.set_position(message.chat.id, "title")
    msg = bot.send_message(message.chat.id, "Введите заголовок")
    keys = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(text='Мне не нужен заголовок', callback_data='without_title ' + msg.message_id)
    keys.add(key)
    bot.edit_message_text(text="Введите заголовок", chat_id=message.chat.id,
                          reply_markup=keys)


def without_title(call):
    bot_action.set_position(user_id=call.message.chat.id, position='text')
    bot.delete_message(call.message.chat.id, call.data.split()[1])
    bot.send_message(call.message.chat.id, 'Введите текст')


def self_destruction(message):
    posts = models.Thread.objects.filter(user_id=message.chat.id)
    user = models.User.objects.get(user_id=message.chat.id)
    for post in posts:
        post.delete()

    user.description = 'пользователь самоуничтожился бум'


def title(message):
    post = bot_action.create_post(user_id=message.chat.id, title=message.text, text='')
    bot_action.set_position(user_id=message.chat.id, position='text ' + post.id)


def text(message):
    post = models.Thread.objects.get(id=bot_action.get_position(user_id=message.chat.id).split()[-1])
    post.text = message.text
    post.save()
    bot_action.set_position(user_id=message.chat.id, position='menu')
    bot.send_message(message.chat.id, '**' + post.title + '**' + '\n\n' + post.text)


def menu(message):
    if message.data:  # if across call
        message = message.message  # for don't copy the same code but only with call.message instead of message

    msg = bot.send_message(message.chat.id, "Меню", )
    buttons = {
        "Мои посты": "all_my_posts " + msg.message_id,
        "Самоуничтожение": "self_destruction " + msg.message_id,
        "Создать новый пост": "create_post " + msg.message_id
    }
    keys = types.InlineKeyboardMarkup()
    for button in buttons:
        key = types.InlineKeyboardButton(text=button, callback_data=buttons[button])
        keys.add(key)

    bot.edit_message_text(text="Меню", chat_id=message.chat.id, message_id=msg.message_id, reply_markup=keys)


def all_my_posts(call=None, message=None):
    if call:
        bot.delete_message(call.message.chat.id, call.data.split()[1])
        msg = bot.send_message(call.message.chat.id, text="Все ваши посты",)
        posts = models.Thread.objects.filter(user__user_id=call.message.chat.id)
        keys = types.InlineKeyboardMarkup()
        for post in posts:
            key = types.InlineKeyboardButton(text=post.title, callback_data='post '+str(post.id))
            key_delete = types.InlineKeyboardButton(text="Удалить этот пост",
                                                    callback_data='delete ' + str(post.id))
            keys.add(key)
            keys.add(key_delete)
        bot.edit_message_text(text="Все ваши посты",
                              message_id=msg.message_id,
                              chat_id=call.message.chat.id,
                              reply_markup=keys)
    if message:
        ...


def get_post(call):
    post = models.Thread.objects.get(call.data.split()[1])
    bot.delete_message(call.message.chat.id, call.data.split()[2])
    bot.send_message(call.message.chat.id, '**' + post.title + '**\n\n' + post.text)


@csrf_exempt
def webhook(request):
    # with open('dump.pickle', 'w') as f:
    #     pickle.dump(request, f)
    print(request.body, '\n\n\n', dir(request), '\n\n\nДЕКОДЕ!!!', str(request.body.decode(encoding='utf-8'),))
    update = types.Update.de_json(request.body.decode(encoding='utf-8'))
    # update = str(request.body.decode(encoding='utf-8'))
    bot.process_new_updates([update])
    return JsonResponse({"ok": "POST request processed"})

# TODO: наканецта вспомнить как эти поганые кнопки делаются, но это уже завтра!

@bot.message_handler(content_types=['text'])
def command_router(message):
    status = bot_action.get_position(message.chat.id)
    commands = {
        'start': start,
        'menu': menu,
        'new_post': new_post,
        'all_my_posts': all_my_posts,
        'self_destruction': self_destruction
    }
    statuses = {
        'title': title,
        'text': text,
        'menu': menu,
    }
    if status != 'start' and message.text[:-1] not in commands:
        print(status)
        statuses[status](message)
    else:
        print(message.text[1:])
        commands[message.text[1:]](message)


@bot.callback_query_handler(func=lambda call: True)
def call_back(call):
    if call.message:
        calls = {
            'no': None,
            'menu': menu,
            'post': get_post
        }
        calls[call.data.split()[0]](call)
