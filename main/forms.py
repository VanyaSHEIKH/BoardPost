from django import forms
from django.core.exceptions import ValidationError
from .models import *


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'author',
            'rating',
            'title',
            'category',
            'text',
        ]

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        text = cleaned_data.get('text')
        if title is not None and len(title) < 5:
            raise ValidationError({
                "title": "Заголовок не может быть меньше 5 символов"
            })
        if text == title:
            raise ValidationError("Заголовок не может быть идентичен содержанию")
        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']