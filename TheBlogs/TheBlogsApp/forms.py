from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Count

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
    text = forms.CharField(label="Text", widget=forms.Textarea(attrs={"placeholder": "Input your blog post"}))

class FilterForm(forms.Form):
    all_authors = User.objects.all().annotate(num_posts=Count("blog_posts")).filter(num_posts__gt=0).order_by('username')
    author = forms.ChoiceField(
            choices=[(-1, "")] + list(map(lambda user: (user.id, user.username), all_authors)),
            label="Author",
            required=False)
    date = forms.DateField(label="Date", required=False, widget=forms.SelectDateWidget())
    title = forms.CharField(label="Title", required=False)
    

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields["author"].widget.attrs["onchange"] = "form.requestSubmit();"
        self.fields["date"].widget.attrs["onchange"] = "form.requestSubmit();"
        self.fields["title"].widget.attrs["onchange"] = "form.requestSubmit();"

class CommentForm(forms.Form):
    text = forms.CharField(label="Your Comment", widget=forms.Textarea(attrs={"rows":"5", "placeholder": "Input your comment"}))

class DeletePostForm(forms.Form):
    post_id = forms.IntegerField(widget=forms.HiddenInput())

class DeleteCommentForm(forms.Form):
    comment_id = forms.IntegerField(widget=forms.HiddenInput())