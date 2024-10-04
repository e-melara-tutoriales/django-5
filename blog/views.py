from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post

def post_list(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 3)
    page_numer = request.GET.get('page', 1)
    posts_list = paginator.page(page_numer)

    return render(request, 'blog/post/list.html', {
        'posts': posts_list
    })

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status = Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    return render(request, 'blog/post/detail.html', {'post': post})
