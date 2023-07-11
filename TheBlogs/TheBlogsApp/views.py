from django.shortcuts import render
from django.http import HttpResponse
from .models import BlogPost
from .config import blogs_per_page

def blog_list(request):
    blogs = BlogPost.objects.order_by('creation_date')[:blogs_per_page]
    context = { 'blogs': blogs }
    return render(request, 'index.html', context)

def blog(request):
    return HttpResponse("Blog")

def authors(request):
    return HttpResponse("Authors")

def search(request):
    return HttpResponse("Search")

def login(request):
    return HttpResponse("Login")