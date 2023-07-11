import json
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Category, Post, DynamicModel, FieldModel
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from user.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import UploadFileForm
import xml.etree.ElementTree as ET
from .importfile import extract_fields_from_json, extract_element_names_and_types
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

def mapping_tables(request):
    dynamic_models = DynamicModel.objects.all()
    return render(request, 'docs/mapping_tables.html', {'dynamic_models': dynamic_models})

def upload_template(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            input_file = request.FILES['file']
            table_name = request.POST['table_name']
            input_file_extension = input_file.name
            content = input_file.read()
            
            if input_file_extension.endswith('.json'):
                fields = extract_fields_from_json(content)
            elif input_file_extension.endswith('.xsd'):
                fields = extract_element_names_and_types(content)
            else:
                print('Formato del file non supportato.')
                fields = None

            #Create_table(table_name, fields)
            if table_name and fields:
                dynamic_model = DynamicModel.objects.create(name=table_name)
                for field in fields:
                    field_name = field.get('name')
                    data_type = field.get('type')
                    if field_name and data_type:
                        try:
                            FieldModel.objects.create(dynamic_model=dynamic_model, name=field_name, data_type=data_type)
                        except IntegrityError as e:
                            pass
                return redirect('docs-mapping-detail', dynamic_model.id)  # Redirigi all'elenco delle tabelle create
    else:
        form = UploadFileForm()
    return render(request, 'docs/upload_template.html', {'form': form})

def mapping_detail(request, table_id):
    dynamic_models = DynamicModel.objects.all()
    dynamic_model = DynamicModel.objects.get(id=table_id)
    fields = FieldModel.objects.filter(dynamic_model=dynamic_model)
    # Esegui altre operazioni di visualizzazione e modifica dei valori della tabella
    if request.method == "POST":
        data = request.POST

        #button = data.get(name)
        if 'delete_template' not in request.POST:
            field_id = data.get('delete_field')
            field = FieldModel.objects.get(id=field_id)
            field.delete()
        else: 
            template_id = data.get('delete_template')
            template = DynamicModel.objects.get(id=template_id)
            template.delete()
            return render(request, 'docs/mapping_tables.html', {'dynamic_models': dynamic_models})
    return render(request, 'docs/mapping_details.html', {'dynamic_model': dynamic_model, 'fields': fields})

@login_required
def questions(request):
    context = {
        'questions' : Post.objects.all(),
        'latest_update' : Post.objects.latest('date_posted').date_posted
    }
    return render(request, 'docs/questions.html', context)

def mapping_detail_update(request, table_id):
    dynamic_model = DynamicModel.objects.get(id=table_id)
    fields = FieldModel.objects.filter(dynamic_model=dynamic_model)
    return render(request, 'docs/mapping_edit.html', {'dynamic_model': dynamic_model, 'fields': fields})

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
