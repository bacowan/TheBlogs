from django.shortcuts import render
from django.http import HttpResponse

def blog_list(request):
    return HttpResponse("Blog List")

def blog(request):
    return HttpResponse("Blog")

def authors(request):
    return HttpResponse("Authors")

def search(request):
    return HttpResponse("Search")

def login(request):
    return HttpResponse("Login")