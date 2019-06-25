from comm_bot import models


def create_user(name, login, user_id, description='блохир'):
    models.User.objects.create(name=name, login=login, id=user_id, description=description)# TODO: мб сюда придётца пкакую-нибдуь проверочку пришпендюрить


def create_post(user_id, title, text):
    user = models.User.objects.get(id=user_id)
    post = models.Thread.objects.create(user=user, title=title, text=text)
    return post.id


def delete_post(user_id, thread_id):
    thread = models.Thread.objects.get(id=thread_id)
    thread.delete()


def self_destruction(user_id):
    user = models.User.objects.get(id=user_id)
    login = user.login
    name = user.name
    user.delete()
    models.User.objects.create(id=user_id, login=login, name=name, description='все посты были самоуничтожены!1!1!')


def get_position(user_id):
    return models.User.objects.get(id=user_id).position


def set_position(user_id, position):
    user = models.User.objects.get(id=user_id)
    user.position = position
    user.save()
