from django.db import models
from django.utils import timezone
import pickle

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=40)
    login = models.CharField(max_length=40)
    user_id = models.CharField(max_length=50)
    date = models.DateTimeField(
        default=timezone.now
    )
    description = models.TextField(default="пирожочек")
    position = models.CharField(max_length=40, default="start")


class Thread(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    title = models.CharField(max_length=80)
    text = models.TextField(default='тред еще не создан')
    date = models.DateTimeField(
        default=timezone.now
    )

    def __str__(self):
        return self.title


class Answer(models.Model):
    user = models.CharField(max_length=20, default='AnonymousUser')
    answer_to = models.IntegerField(default=0)
    answers = models.TextField(default=pickle.dumps([]))
    text = models.TextField()
    date = models.DateTimeField(
        default=timezone.now
    )
    thread = models.ForeignKey("Thread", on_delete=models.CASCADE)

    def add_answer(self, number):
        """
        добавляет ид комментария в self.answers чтобы потом его оттуда достать
        :param number: ид добавляемого в список комментария
        :return: ничево
        """
        if self.answers:
            answers = pickle.loads(eval(self.answers))
            answers.append(number)
            b = pickle.dumps(answers)
            self.answers = str(b)
            self.save()

    @staticmethod
    def make_answer(answer):
        """
        :param answer_id: ид ответа, который создается
        :param number_to: ид ответа, на который создается комментарий
        :return: ничево
        """
        Answer.objects.get(id=answer.answer_to).add_answer(answer.id)

    def __str__(self):
        return self.text
