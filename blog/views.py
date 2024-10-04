from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import EmailPostForm, CommentForm
from .models import Post

class PostListView(ListView):
    queryset = Post.objects.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 3)
    page_numer = request.GET.get('page', 1)

    try:
        posts_list = paginator.page(page_numer)
    except PageNotAnInteger:
        posts_list = paginator.page(1)
    except EmptyPage:
        posts_list = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {
        'posts': posts_list
    })

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = (
                f"{cd['name']} recommends you read {post.title}",
                f"Read {post.title} at {post_url}",
            )

            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )

            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {
        'post': post,
        'form': form,
        'sent': sent
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

    comments = post.comments.filter(active=True)
    form = CommentForm()
    print(f"post: {post}")
    print(f"comments: {form}")
    return render(request, 'blog/post/detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id = post_id,
        status = Post.Status.PUBLISHED
    )
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(request, 'blog/post/comment.html', {
        'post': post,
        'comment': comment,
        'form': form
    })
