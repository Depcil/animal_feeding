from django import forms
from django.core.exceptions import ValidationError

from .models import Animal

# Ограничение размера загружаемого фото, байт.
MAX_PHOTO_SIZE = 2 * 1024 * 1024


class AnimalPhotoForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ("photo",)
        widgets = {
            "photo": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),
        }
        help_texts = {
            "photo": "Изображение JPG, PNG или WebP, не больше 2 МБ.",
        }

    def clean_photo(self):
        # Что файл действительно изображение, проверяет сам ImageField
        # (через Pillow); здесь дополнительно ограничивается размер.
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > MAX_PHOTO_SIZE:
            raise ValidationError("Файл слишком большой: не больше 2 МБ.")
        return photo
