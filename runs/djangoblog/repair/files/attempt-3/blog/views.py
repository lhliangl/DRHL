from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post


class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'index.html'


class PostDetail(LoginRequiredMixin, generic.DetailView):
    model = Post
    template_name = 'post_detail.html'
