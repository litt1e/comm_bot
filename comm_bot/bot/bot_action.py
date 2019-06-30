#*- coding: utf-8 -*-
from comm_bot import models


def create_user(name, login, user_id, description='блохир'):
    try:
        user = models.User.objects.get(id=user_id)
    except models.User.DoesNotExist:
        user = models.User.objects.create(name=name,
                                          login=login,
                                          id=user_id,
                                          description=description)
    return user, 'created'


def create_post(user_id, title, text):
    user = models.User.objects.get(id=user_id)
    post = models.Thread.objects.create(user=user,
                                        title=title,
                                        text=text)
    return post


def delete_post(thread_id):
    thread = models.Thread.objects.get(id=thread_id)
    thread.delete()


def self_destruction(user_id):
    user = models.User.objects.get(id=user_id)
    login = user.login
    name = user.name
    user.delete()
    models.User.objects.create(id=user_id,
                               login=login,
                               name=name,
                               description='все посты были самоуничтожены!1!1!')


def get_position(user_id):
    try:
        pos = models.User.objects.get(id=user_id).position
    except models.User.DoesNotExist:
        pos = 'nothing'
        return pos
    else:
        return pos



def set_position(user_id, position):
    user = models.User.objects.get(id=user_id)
    user.position = position
    user.save()


def is_there_login(login):
    try:
        models.User.objects.get(login=login)
    except models.User.DoesNotExist:
        return False
    else:
        return True
