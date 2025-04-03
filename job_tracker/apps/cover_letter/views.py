"""
Views for cover letter generation and management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import CoverLetterTemplate, UserCoverLetterTemplate, GeneratedCoverLetter
from .generator import generate_cover_letter, load_default_templates
from ..linkedin_integration.models import LinkedInJob

import logging
import json

logger = logging.getLogger(__name__)

@login_required
def cover_letter_templates(request):
    """
    View for managing cover letter templates.
    """
    # Get system templates
    system_templates = CoverLetterTemplate.objects.all()
    
    # Get user templates
    user_templates = UserCoverLetterTemplate.objects.filter(user=request.user)
    
    return render(request, 'cover_letter/templates.html', {
        'system_templates': system_templates,
        'user_templates': user_templates
    })

@login_required
def create_template(request):
    """
    View for creating a new cover letter template.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        content = request.POST.get('content')
        is_default = request.POST.get('is_default') == 'on'
        
        if not name or not content:
            messages.error(request, "Name and content are required")
            return redirect('create_template')
        
        # If setting as default, unset other defaults
        if is_default:
            UserCoverLetterTemplate.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Create template
        template = UserCoverLetterTemplate.objects.create(
            user=request.user,
            name=name,
            description=description,
            content=content,
            is_default=is_default
        )
        
        messages.success(request, f"Template '{name}' created successfully")
        return redirect('cover_letter_templates')
    
    return render(request, 'cover_letter/create_template.html')

@login_required
def edit_template(request, template_id):
    """
    View for editing a cover letter template.
    """
    template = get_object_or_404(UserCoverLetterTemplate, id=template_id, user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        content = request.POST.get('content')
        is_default = request.POST.get('is_default') == 'on'
        
        if not name or not content:
            messages.error(request, "Name and content are required")
            return redirect('edit_template', template_id=template_id)
        
        # If setting as default, unset other defaults
        if is_default and not template.is_default:
            UserCoverLetterTemplate.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Update template
        template.name = name
        template.description = description
        template.content = content
        template.is_default = is_default
        template.save()
        
        messages.success(request, f"Template '{name}' updated successfully")
        return redirect('cover_letter_templates')
    
    return render(request, 'cover_letter/edit_template.html', {
        'template': template
    })

@login_required
def delete_template(request, template_id):
    """
    View for deleting a cover letter template.
    """
    template = get_object_or_404(UserCoverLetterTemplate, id=template_id, user=request.user)
    
    if request.method == 'POST':
        template_name = template.name
        template.delete()
        messages.success(request, f"Template '{template_name}' deleted successfully")
    
    return redirect('cover_letter_templates')

@login_required
def generate_cover_letter_view(request, job_id):
    """
    View for generating a cover letter for a specific job.
    """
    job = get_object_or_404(LinkedInJob, id=job_id)
    
    # Check if user has a resume
    if not hasattr(request.user, 'profile') or not request.user.profile.resume:
        messages.error(request, "Please upload your resume first")
        return redirect('profile_edit')
    
    # Get templates
    system_templates = CoverLetterTemplate.objects.all()
    user_templates = UserCoverLetterTemplate.objects.filter(user=request.user)
    
    # Check if already generated
    existing_letter = GeneratedCoverLetter.objects.filter(user=request.user, job=job).first()
    
    if request.method == 'POST':
        template_type = request.POST.get('template_type')
        template_id = request.POST.get('template_id')
        
        try:
            # Generate cover letter
            resume_path = request.user.profile.resume.path
            
            if template_type == 'system' and template_id:
                template = get_object_or_404(CoverLetterTemplate, id=template_id)
                template_content = template.content
                template_used = template
                user_template_used = None
            elif template_type == 'user' and template_id:
                template = get_object_or_404(UserCoverLetterTemplate, id=template_id, user=request.user)
                template_content = template.content
                template_used = None
                user_template_used = template
            else:
                # Use default template
                template_content = None
                template_used = None
                user_template_used = None
            
            # Generate cover letter
            cover_letter_content = generate_cover_letter(
                resume_path=resume_path,
                job_description=job.description,
                applicant_name=request.user.get_full_name() or request.user.username,
                job_title=job.title,
                company_name=job.company
            )
            
            # Save or update generated cover letter
            if existing_letter:
                existing_letter.content = cover_letter_content
                existing_letter.template_used = template_used
                existing_letter.user_template_used = user_template_used
                existing_letter.save()
                messages.success(request, "Cover letter updated successfully")
            else:
                GeneratedCoverLetter.objects.create(
                    user=request.user,
                    job=job,
                    content=cover_letter_content,
                    template_used=template_used,
                    user_template_used=user_template_used
                )
                messages.success(request, "Cover letter generated successfully")
            
            return redirect('view_cover_letter', job_id=job.id)
            
        except Exception as e:
            logger.exception(f"Error generating cover letter: {str(e)}")
            messages.error(request, f"Error generating cover letter: {str(e)}")
            return redirect('generate_cover_letter', job_id=job.id)
    
    return render(request, 'cover_letter/generate.html', {
        'job': job,
        'system_templates': system_templates,
        'user_templates': user_templates,
        'existing_letter': existing_letter
    })

@login_required
def view_cover_letter(request, job_id):
    """
    View for viewing a generated cover letter.
    """
    job = get_object_or_404(LinkedInJob, id=job_id)
    cover_letter = get_object_or_404(GeneratedCoverLetter, user=request.user, job=job)
    
    return render(request, 'cover_letter/view.html', {
        'job': job,
        'cover_letter': cover_letter
    })

@login_required
def edit_cover_letter(request, job_id):
    """
    View for editing a generated cover letter.
    """
    job = get_object_or_404(LinkedInJob, id=job_id)
    cover_letter = get_object_or_404(GeneratedCoverLetter, user=request.user, job=job)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if not content:
            messages.error(request, "Cover letter content is required")
            return redirect('edit_cover_letter', job_id=job.id)
        
        # Update cover letter
        cover_letter.content = content
        cover_letter.save()
        
        messages.success(request, "Cover letter updated successfully")
        return redirect('view_cover_letter', job_id=job.id)
    
    return render(request, 'cover_letter/edit.html', {
        'job': job,
        'cover_letter': cover_letter
    })

@login_required
def download_cover_letter(request, job_id):
    """
    View for downloading a cover letter as a text file.
    """
    job = get_object_or_404(LinkedInJob, id=job_id)
    cover_letter = get_object_or_404(GeneratedCoverLetter, user=request.user, job=job)
    
    # Create response with cover letter content
    response = HttpResponse(cover_letter.content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="cover_letter_{job.company}_{job.title}.txt"'
    
    return response

@login_required
def api_generate_cover_letter(request):
    """
    API endpoint for generating a cover letter.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not hasattr(request.user, 'profile') or not request.user.profile.resume:
        return JsonResponse({'error': 'No resume found'}, status=400)
    
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        
        if not job_id:
            return JsonResponse({'error': 'Job ID is required'}, status=400)
        
        job = LinkedInJob.objects.get(id=job_id)
        resume_path = request.user.profile.resume.path
        
        # Generate cover letter
        cover_letter_content = generate_cover_letter(
            resume_path=resume_path,
            job_description=job.description,
            applicant_name=request.user.get_full_name() or request.user.username,
            job_title=job.title,
            company_name=job.company
        )
        
        return JsonResponse({
            'success': True,
            'cover_letter': cover_letter_content
        })
    except LinkedInJob.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
    except Exception as e:
        logger.exception(f"Error generating cover letter: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
