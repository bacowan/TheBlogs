import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from datetime import date
from .models import BlogPost, Comment
from .config import blogs_per_page, comments_per_page
from .forms import CommentForm, DeleteCommentForm, DeletePostForm, FilterForm, SigninForm, NewBlogPostForm, SignupForm
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
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = blog.comments.create(
                    text=form.cleaned_data['text'],
                    author=request.user,
                    creation_date=datetime.datetime.now()
                )
                comment.save()
                AppStream().update("comments.html", get_comments_context(blog, 0, request), id="commentsframe")
        else:
            form = CommentForm()
        context = {
            'blog': blog,
            'comment_form': form,
            'is_signed_in': request.user.is_authenticated,
            'username': request.user.username,
            'is_user_author': request.user.id == blog.author.id,
            'delete_post_form': DeletePostForm(initial={'post_id':id})
        }
        return render(request, 'single_post/index.html', context)
    else:
        return HttpResponse(f"Could not find blog post with ID {id}")

def comments(request, id):
    blog = BlogPost.objects.get(pk=id)
    if blog != None:
        page = int(request.GET.get("page", 0))
        return render(request, 'comments.html', get_comments_context(blog, page, request))
    else:
        return HttpResponse(f"Could not find blog post with ID {id}")

def get_comments_context(blog, page, request):
    comments = blog.comments.order_by('-creation_date')[page*comments_per_page:(page+1)*comments_per_page]
    return {
        'blog': blog,
        'page': page,
        'comments': list(map(lambda comment: {
            'comment': comment,
            'form': DeleteCommentForm(initial={'comment_id': comment.id}),
            'is_user_author': request.user.id == comment.author.id,
        }, comments)),
        'are_newer_comments': page > 0,
        'are_older_comments': blog.comments.count() > (page+1)*comments_per_page
    }

def delete_blog_post(request):
    if request.method == "POST":
        form = DeletePostForm(request.POST)
        if form.is_valid():
            try:
                blog = BlogPost.objects.get(pk=form.cleaned_data['post_id'])
                if blog.author.id == request.user.id:
                    blog.delete()
                else:
                    return HttpResponse("Unauthorized")
            except:
                pass
    return redirect('blog_list')

def delete_comment(request):
    if request.method == "POST":
        form = DeleteCommentForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data['comment_id'])
            try:
                comment = Comment.objects.get(pk=form.cleaned_data['comment_id'])
                if comment.author.id == request.user.id:
                    comment.delete()
                    AppStream().update("comments.html", get_comments_context(comment.blog_post, 0, request), id="commentsframe")
                else:
                    return HttpResponse("Unauthorized")
            except:
                pass
    return HttpResponse("")

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
        return HttpResponse("Please sign in before making a post")

    if request.method == "POST":
        form = NewBlogPostForm(request.POST)
        if form.is_valid():
            blogPost = BlogPost(
                title=form.cleaned_data['title'],
                text=form.cleaned_data['text'],
                author=request.user,
                creation_date=datetime.datetime.now()
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
        try:
            date_val = datetime.datetime.strptime(date, '%Y%m%d')
            args += "&date=" + date
            blog_query = blog_query.filter(creation_date__lt=date_val + datetime.timedelta(days=1)).filter(creation_date__gt=date_val)
        except Exception as e:
            pass

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