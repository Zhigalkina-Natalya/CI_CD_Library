from django import forms
from .models import Author, Book
from django.core.exceptions import ValidationError


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'birth_date']

    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите имя'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите фамилию'})
        self.fields['birth_date'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите дату рождения'})

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        if Author.objects.filter(first_name=first_name, last_name=last_name).exists():
            raise ValidationError('Автор с таким именем и фамилией уже существует.')

        return cleaned_data

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'publication_date', 'author']

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите название книги'})
        self.fields['publication_date'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Введите дату публикации'})
        self.fields['author'].widget.attrs.update({'class': 'form-control'})