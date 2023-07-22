import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from turbo.shortcuts import render_frame_string, render_frame
from datetime import date
from .models import BlogPost
from .config import blogs_per_page
from .forms import FilterForm, SigninForm, NewBlogPostForm, SignupForm
from .streams import AppStream

def blog_list(request):
    context = {
        'is_signed_in': request.user.is_authenticated,
        'username': request.user.username,
        'filter_form': FilterForm()
    }
    return render(request, 'clean_blog/index.html', context)

def blog(request, id):
    blog = BlogPost.objects.get(pk=id)
    if blog != None:
        context = {
            'blog': blog
        }
        return render(request, 'single_post/index.html', context)
    else:
        return HttpResponse(f"Could not find blog post with ID {id}")
        # TODO: return 404

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

def get_filtered_blog_context(author_id, date, title, page):
    blog_query = BlogPost.objects.order_by('-creation_date')

    args = ""

    author_id = int(author_id)
    if author_id != -1:
        args += "&author=" + str(author_id)
        blog_query = blog_query.filter(author=author_id)

    if date != None:
        print(date)
        try:
            date_val = datetime.datetime.strptime(date, '%Y%m%d').date()
            args += "&date=" + date
            print(date_val)
            blog_query = blog_query.filter(creation_date=date_val)
        except Exception as e:
            print(str(e))

    if title != None and title != "":
        args += "&title=" + title
        blog_query = blog_query.filter(title__icontains=title)

    previous_args = "page=" + str(page - 1) + args
    next_args = "page=" + str(page + 1) + args

    blogs = blog_query[page*blogs_per_page:(page+1)*blogs_per_page]
    return {
        'previous_args': previous_args,
        'next_args': next_args,
        'blogs': blogs,
        'are_newer_pages': page > 0,
        'are_older_pages': blog_query.count() > (page+1)*blogs_per_page
    }

def filtered_blogs(request):
    author_id = request.GET.get("author", -1)
    date = request.GET.get("date", None)
    title = request.GET.get("title", None)
    page = int(request.GET.get("page", 0))
    context = get_filtered_blog_context(
        author_id=author_id,
        date=date,
        title=title,
        page=page
    )
    return render(request, 'filtered_blogs.html', context)

def perform_filter_blogs(request):
    form = FilterForm(request.POST)
    form.is_valid() # force the data to clean
    author_id = form.cleaned_data.get("author", -1)
    date = form.cleaned_data.get("date", None)
    if date != None:
        date = date.strftime('%Y%m%d')
    title = form.cleaned_data.get("title", None)
    context = get_filtered_blog_context(
        author_id=author_id,
        date=date,
        title=title,
        page=0
    )
    AppStream().update("filtered_blogs.html", context, id="postsframe")
    return HttpResponse("")