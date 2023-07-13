from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import BlogPost
from .config import blogs_per_page
from .forms import SigninForm, NewBlogPostForm, SignupForm

def blog_list(request):
    blogs = BlogPost.objects.order_by('-creation_date')[:blogs_per_page]
    context = {
        'blogs': blogs,
        'is_signed_in': request.user.is_authenticated,
        'username': request.user.username
    }
    return render(request, 'clean_blog/index.html', context)

def login(request):
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            user = authenticate(request,
                                username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                django_login(request, user)
                return redirect('blog_list')
            else:
                form.add_error(None, ValidationError("Incorrect username or password"))
    else:
        form = SigninForm()

    context = {
        'user_form': form
    }
    return render(request, 'login/index.html', context)

def logout(request):
    django_logout(request)
    return redirect('blog_list')

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'])
            user.save()
            django_login(request, user)
            return redirect('blog_list')
    else:
        form = SignupForm()
    
    context = {
        'user_form': form
    }
    return render(request, 'signup/index.html', context)

def new_post(request):
    if not request.user.is_authenticated:
        # TODO: show an error page
        pass

    if request.method == "POST":
        form = NewBlogPostForm(request.POST)
        if form.is_valid():
            blogPost = BlogPost(
                title=form.cleaned_data['title'],
                text=form.cleaned_data['text'],
                author=request.user,
                creation_date=date.today()
            )
            blogPost.save()
            return redirect('blog_list')
    else:
        form = NewBlogPostForm()
    
    context = {
        'post_form': form
    }
    return render(request, 'new_post/index.html', context)