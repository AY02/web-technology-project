from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Project
from .forms import ProjectCreationForm

@login_required
def dashboard_view(request, project_id=None):
    if project_id:
        current_project = get_object_or_404(Project, id=project_id, owner=request.user)
    else:
        current_project = Project.objects.filter(owner=request.user, parent__isnull=True).first()
    
    subprojects = current_project.subprojects.all() if current_project else []
    parent_project = current_project.parent if current_project else None
    
    context = {
        'current_project': current_project,
        'subprojects': subprojects,
        'parent_project': parent_project,
        'creation_form': ProjectCreationForm(),
    }
    return render(request, 'projects/dashboard.html', context)

@login_required
@require_POST
def create_subproject(request, parent_id):
    """
    After receiving data from the form we create the new subproject.
    """

    # the project to which the user wants to add a subproject needs to be of its property 
    parent_project = get_object_or_404(Project, id=parent_id, owner=request.user)
    
    form = ProjectCreationForm(data=request.POST, user=request.user, parent_project=parent_project)
    if form.is_valid():
        form.save()
        
    # refreshing the page of the parent to see the new child
    return redirect('dashboard_project', project_id=parent_project.id)