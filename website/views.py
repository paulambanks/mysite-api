from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.mail import send_mail, BadHeaderError
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Post
from .forms import PostForm, ContactForm

# Create your views here.

# posts/views.py


def home(request):
    """The home page introduces user to the blog and allows for registration or login"""
    return render(request, 'home.html')


def about(request):
    """The page containing information about the author, including online CV and PDF download link"""
    return render(request, 'website/about.html')


def posts_list(request):
    """The page with all blog posts, visible to all"""
    template = 'website/post_list.html'
    post_list = Post.objects.filter(status='Published', privacy='General').order_by('-created')
    page = request.GET.get('page', 1)

    paginator = Paginator(post_list, 6)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, template, {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.privacy == 'General':
        return render(request, 'website/post_detail.html', {'post': post})
    elif post.privacy == 'Public' and request.user.is_authenticated:
        return render(request, 'website/post_detail.html', {'post': post})
    else:
        return PermissionDenied


@login_required
def post_draft_list(request):
    """The page with all unpublished yet drafts. Visible only to the admin/staff"""
    template = 'website/post_draft_list.html'
    post_list = Post.objects.filter(status='Draft', author=request.user).order_by('created')

    page = request.GET.get('page', 1)

    paginator = Paginator(post_list, 6)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, template, {'posts': posts})


@login_required
def post_new(request):
    """Create new post is visible only for the admin/staff"""
    template = 'website/post_edit.html'
    if request.method == "POST":
        form = PostForm(request.POST)

        try:
            if form.is_valid():
                if 'cancel' in request.POST:
                    return HttpResponseRedirect(get_success_url())
                else:
                    post = form.save(commit=False)
                    post.author = request.user
                    post.save()
                    return redirect('website:post_detail', pk=post.pk)

        except Exception as e:
            messages.warning(request, 'Post Failed To Save. Error: {}".format(e)')

    else:
        form = PostForm()
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def post_edit(request, pk):  # also post update
    template = 'website/post_edit.html'
    post = get_object_or_404(Post, pk=pk)

    if post.author == request.user:

        if request.method == "POST":
            form = PostForm(request.POST, instance=post)

            try:
                if form.is_valid():
                    if 'cancel' in request.POST:
                        return HttpResponseRedirect(get_success_url())
                    else:
                        post = form.save(commit=False)
                        post.author = request.user
                        post.save()
                        messages.success(request, "Your Post Was Successfully Updated")
                        return redirect('website:post_detail', pk=post.pk)

            except Exception as e:
                messages.warning(request, 'Your Post Was Not Saved Due To An Error: {}.format(e)')

        else:
            form = PostForm(instance=post)

        context = {
            'form': form,
            'post': post,
        }

        return render(request, template, context)
    else:
        raise Http404


def get_success_url():
    """Return page if creating/edition of post was canceled"""
    return reverse('website:posts_list')


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    template = 'website/confirmation_publish.html'

    if post.author == request.user:

        if request.method == "POST":
            post.publish()
            messages.success(request, "This post has been published.")
            return HttpResponseRedirect(reverse('website:posts_list'))

        if request.user != post.author:
            raise PermissionDenied

        context = {
            "post": post
        }

        return render(request, template, context)
    else:
        raise Http404


@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    template = 'website/confirmation_delete.html'

    if post.author == request.user:

        if request.method == "POST":
            post.delete()
            messages.success(request, "This has been deleted.")
            return HttpResponseRedirect(reverse('website:posts_list'))

        if request.user != post.author:
            raise PermissionDenied

        context = {
            "post": post
        }

        return render(request, template, context)
    else:
        raise Http404


def send_email(request):
    """Sends a message to the admin from the user"""
    template = 'website/email.html'
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = request.user.email
            message = form.cleaned_data['message']

            try:
                message = "User {} has sent you a message\n".format(from_email) + message
                send_mail(subject, message, from_email, ['bankspaula576@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')

            return redirect('website:success')

    return render(request, template, {'form': form})


def email_success(request):
    return HttpResponse('Success! Thank you for your message.')