from django.db import models
from django.conf import settings

class BlogPost(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    creation_date = models.DateTimeField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )

    def __str__(self):
        return f'{self.title} by {self.author.username}'
    
class Comment(models.Model):
    text = models.TextField()
    creation_date = models.DateTimeField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    blog_post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    def __str__(self):
        return f'Comment on {self.blog_post.title} by {self.author.username}'