from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Category, Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from user.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
# Create your views here.

categories = [
    {
        'categ_name': 'APIs',
        'categ_description': ' Section overview goes here. Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor.',
        'icon' : 'fa-box fa-fw'
    },
    {
        'categ_name': 'Integrations',
        'categ_description': ' Section overview goes here. Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor.',
        'icon' : 'fa-cogs fa-fw'
    }
]


def home(request):
    context = {
        'categories' : Category.objects.all()
    }
    return render(request, 'docs/home.html', context)

def docs_content(request):
    return render(request, 'docs/main.html')

@login_required
def questions(request):
    context = {
        'questions' : Post.objects.all(),
        'latest_update' : Post.objects.latest('date_posted').date_posted
    }
    return render(request, 'docs/questions.html', context)



class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'docs/questions.html'
    context_object_name = 'questions'
    ordering = ['-date_posted']


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post =self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/questions'

    def test_func(self):
        post =self.get_object()
        if self.request.user == post.author:
            return True
        return False

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('docs-profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'docs/profile.html', context)
