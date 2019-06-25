from django import forms


class Reply(forms.Form):
    text = forms.CharField(widget=forms.Textarea)


class Answer(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    answer_to = forms.IntegerField()
