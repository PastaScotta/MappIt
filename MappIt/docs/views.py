import json
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Category, Post, DynamicModel, FieldModel, ValueModel
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from user.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import UploadFileForm
import xml.etree.ElementTree as ET
from .importfile import extract_fields_from_json, extract_element_names_and_types
# Create your views here.

def home(request):
    context = {
        'categories' : Category.objects.all()
    }
    return render(request, 'docs/home.html', context)

def docs_content(request):
    return render(request, 'docs/main.html')

@login_required
def mapping_tables(request):
    dynamic_models = DynamicModel.objects.all()
    return render(request, 'docs/mapping_tables.html', {'dynamic_models': dynamic_models})

@login_required
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

@login_required
def mapping_detail(request, table_id): 
    dynamic_models = DynamicModel.objects.all()
    dynamic_model = DynamicModel.objects.get(id=table_id)
    fields = FieldModel.objects.filter(dynamic_model=dynamic_model)
    value_models = ValueModel.objects.filter(dynamic_model=table_id).values('code')
    unique_codes = value_models.distinct()
    # Esegui altre operazioni di visualizzazione e modifica dei valori della tabella
    if request.method == "POST":
        data = request.POST
        if 'delete_field' in request.POST:
            field_id = data.get('delete_field')
            field = FieldModel.objects.get(id=field_id)
            field.delete()
            return redirect('docs-mapping-detail' ,dynamic_model.id)
        elif 'edit_field' in request.POST:
            field_id = data.get('field-id')
            field = FieldModel.objects.get(id=field_id)
            new_field_name = data.get('new-field-name')
            new_data_type = data.get('new-field-type')
            field.name = new_field_name
            field.data_type = new_data_type
            field.save()
            return redirect('docs-mapping-detail' ,dynamic_model.id)
        elif 'add_field' in request.POST:  
            field_name = data.get('field-name')
            data_type = data.get('field-type')
            FieldModel.objects.create(dynamic_model=dynamic_model, name=field_name, data_type=data_type)
            return redirect('docs-mapping-detail' ,dynamic_model.id)
        else: 
            template_id = data.get('delete_template')
            template = DynamicModel.objects.get(id=template_id)
            template.delete()
            return render(request, 'docs/mapping_tables.html', {'dynamic_models': dynamic_models})

    return render(request, 'docs/mapping_details.html', {'dynamic_model': dynamic_model, 'fields': fields, 'unique_codes': unique_codes})


@login_required
def mapping_version_detail(request, table_id, code):
    code_value=code 
    dynamic_models = DynamicModel.objects.all()
    dynamic_model = DynamicModel.objects.get(id=table_id)
    value_models = ValueModel.objects.filter(dynamic_model=table_id ,code=code)
    if request.method == "POST":
        data = request.POST
        if 'edit_field' in request.POST:
            field_id = data.get('field-id')
            code = data.get('code')
            value = ValueModel.objects.get(id=field_id)
            new_value = data.get('new-value')
            value.value = new_value
            value.save()
            return redirect('docs-mapping-version-detail', dynamic_model.id,  code)
        else:
            value_models.delete()
            return redirect('docs-mapping-detail' ,dynamic_model.id)
    return render(request, 'docs/mapping_version_details.html', {'dynamic_model': dynamic_model, 'value_models': value_models, 'mapping_code': code})



@login_required
def questions(request):
    context = {
        'questions' : Post.objects.all(),
        'latest_update' : Post.objects.latest('date_posted').date_posted
    }
    return render(request, 'docs/questions.html', context)

@login_required
def mapping_detail_new_version(request, table_id):
    dynamic_model = DynamicModel.objects.get(id=table_id)
    fields = FieldModel.objects.filter(dynamic_model=dynamic_model)
    if request.method == "POST":
        data = request.POST
        #print(data)
        code = data.get('code')
        fields = data.getlist('field-name')
        values = data.getlist('field-value')
        dic_from_lists = dict(zip(fields, values))
        for key, value in dic_from_lists.items():
            ValueModel.objects.create(dynamic_model=dynamic_model, code=code, name=key, value=value)
        return redirect('docs-mapping-detail', dynamic_model.id) 



    return render(request, 'docs/mapping_version_create.html', {'dynamic_model': dynamic_model, 'fields': fields})

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
