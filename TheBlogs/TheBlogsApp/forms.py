from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class SigninForm(forms.Form):
    username = forms.CharField(label="Username", max_length=20, widget=forms.TextInput(attrs={"placeholder": "username"}))
    password = forms.CharField(label="Password", max_length=30, widget=forms.PasswordInput(attrs={"placeholder": "password"}))

class SignupForm(forms.Form):
    username = forms.CharField(label="Username", max_length=20, widget=forms.TextInput(attrs={"placeholder": "username"}))
    password = forms.CharField(label="Password", max_length=30, widget=forms.PasswordInput(attrs={"placeholder": "password"}))
    repeat_password = forms.CharField(label="Repeat Password", max_length=30, widget=forms.PasswordInput(attrs={"placeholder": "repeat password"}))

    def clean(self):
        cleaned_data = super().clean()
        cleaned_password = cleaned_data.get("password")
        cleaned_repeat_password = cleaned_data.get("repeat_password")
        if cleaned_password != cleaned_repeat_password:
            raise ValidationError("Passwords must match")
            
        return cleaned_data

class NewBlogPostForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    text = forms.CharField(label="Text", widget=forms.Textarea(attrs={"rows":"15", "placeholder": "Input your blog post"}))

class FilterForm(forms.Form):
    author = forms.ChoiceField(
            choices=[(-1, "")] + list(map(lambda user: (user.id, user.username), filter(lambda user : user.blog_posts.exists(), User.objects.all()))),
            label="Author",
            required=False)
    date = forms.DateField(label="Date", required=False, widget=forms.SelectDateWidget())
    title = forms.CharField(label="Title", required=False)
    

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["author"].widget.attrs["onchange"] = "form.requestSubmit();"
        self.fields["date"].widget.attrs["onchange"] = "form.requestSubmit();"
        self.fields["title"].widget.attrs["onchange"] = "form.requestSubmit();"