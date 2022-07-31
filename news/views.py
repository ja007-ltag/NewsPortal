from django.views.generic import ListView, DetailView
from .models import Post


class PostList(ListView):
    model = Post
    ordering = '-date'
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'


class PostDetail(DetailView):
    model = Post
    template_name = 'news/news_detail.html'
    context_object_name = 'news_detail'
