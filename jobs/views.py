from django.shortcuts import render, get_object_or_404
from .models import Job

def job_list(request):
    qs = Job.objects.all().order_by('-created_at')
    return render(request, 'jobs/job_list.html', {'jobs': qs})

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    return render(request, 'jobs/job_detail.html', {'job': job})
