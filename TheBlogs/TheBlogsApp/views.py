from django.shortcuts import render
from django.http import HttpResponse
from .models import BlogPost
from .config import blogs_per_page

def blog_list(request):
    blogs = BlogPost.objects.order_by('creation_date')[:blogs_per_page]
    context = { 'blogs': blogs }
    return render(request, 'clean_blog/index.html', context)

def login(request):
    return HttpResponse("Login")

def signup(request):
    return HttpResponse("Signup")