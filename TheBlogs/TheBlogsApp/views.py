from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django import forms
from django.core.exceptions import ValidationError
from turbo.shortcuts import render_frame_string, render_frame
from datetime import date
from .models import BlogPost
from .config import blogs_per_page
from .forms import SigninForm, NewBlogPostForm, SignupForm

def blog_list(request):
    author = int(request.POST.get("author", -1))
    date = request.POST.get("date", "")
    title = request.POST.get("title", "")
    # TODO: the actual filter
    context = {
        'is_signed_in': request.user.is_authenticated,
        'username': request.user.username,
        'authors': filter(lambda user : user.blog_posts.exists(), User.objects.all()),
        'selected_author': author,
        'selected_date': date,
        'selected_title': title
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

def filtered_blogs(request):
    page = int(request.GET.get("page", 0))
    blogs = BlogPost.objects.order_by('-creation_date')[page*blogs_per_page:(page+1)*blogs_per_page]
    context = {
        'page': page,
        'blogs': blogs,
        'are_newer_pages': page > 0,
        'are_older_pages': BlogPost.objects.count() > (page+1)*blogs_per_page
    }
    return render(request, 'filtered_blogs.html', context)
