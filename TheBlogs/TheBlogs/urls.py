"""
URL configuration for TheBlogs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from TheBlogsApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.blog_list, name='blog_list'),
    path('blog/<int:id>/', views.blog),
    path('blog/<int:id>/comments', views.comments),
    path('delete-blog-post/', views.delete_blog_post),
    path('delete-comment/', views.delete_comment),
    path('index', views.blog_list),
    path('login/', views.login),
    path('logout/', views.logout),
    path('signup/', views.signup),
    path('new-post/', views.new_post),
    path("filtered-blogs/", views.filtered_blogs),
    path("perform-filter-blogs/", views.perform_filter_blogs)
]
