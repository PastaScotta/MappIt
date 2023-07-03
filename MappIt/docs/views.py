import json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Category, Post, DynamicModel, FieldModel
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from user.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import UploadFileForm
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
            file = request.FILES['file']
            table_name = request.POST['table_name']
            # Esegui il codice per analizzare il file XSD o JSON e creare le tabelle nel database
            # Puoi utilizzare librerie come xmltodict o json per analizzare il file
            if file.name.endswith('.xsd'):
                # Codice per analizzare il file XSD e creare le tabelle nel database
                pass
            elif file.name.endswith('.json'):
                fields = []
                def process_dict(data, prefix=''):
                    for key, value in data.items():
                        field_name = f'{prefix}{key}' if prefix else key

                        if isinstance(value, dict):
                            process_dict(value, prefix=field_name + '.')
                        else:
                            field_type = type(value).__name__
                            fields.append({'name': field_name, 'type': field_type})
                try:                
                    # Legge il contenuto del file JSON
                    json_content = file.read().decode('utf-8')
                    #file.close()

                    json_data = json.loads(json_content)
                    process_dict(json_data)
                except json.JSONDecodeError as e:
                    print(f'Errore durante il parsing del file JSON: {e}')
                    # Carica lo schema JSON
                    #schema = json.loads(json_content)
            
                    # Estrae i campi e i relativi tipi dallo schema JSON
                    #fields = extract_fields_from_json_schema(schema)

                if table_name and fields:
                    dynamic_model = DynamicModel.objects.create(name=table_name)
                    for field in fields:
                        field_name = field.get('name')
                        data_type = field.get('type')
                        if field_name and data_type:
                            FieldModel.objects.create(dynamic_model=dynamic_model, name=field_name, data_type=data_type)
                    return redirect('docs-mapping-detail', dynamic_model.id)  # Redirigi all'elenco delle tabelle create
                else:
                        # Il file JSON non ha le informazioni necessarie
                    return redirect('docs-home')
    else:
        form = UploadFileForm()
    return render(request, 'docs/upload_template.html', {'form': form})

def mapping_detail(request, table_id):
    dynamic_model = DynamicModel.objects.get(id=table_id)
    fields = FieldModel.objects.filter(dynamic_model=dynamic_model)
    # Esegui altre operazioni di visualizzazione e modifica dei valori della tabella
    return render(request, 'docs/mapping_details.html', {'dynamic_model': dynamic_model, 'fields': fields})

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
