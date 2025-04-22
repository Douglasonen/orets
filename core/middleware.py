from django.shortcuts import redirect
from django.urls import reverse
from .models import BusinessProfile
from django.contrib import messages
# middleware.py
from threading import local
from django.conf import settings

_thread_locals = local()

def get_current_request():
    """Retrieve the request object from thread-local storage."""
    return getattr(_thread_locals, 'request', None)

class ThreadLocalRequestMiddleware:
    """Stores the current request in thread-local storage."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        _thread_locals.request = request
        response = self.get_response(request)
        return response

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            'business_profile',
            'logout',
            'complete_profile',
            'static',
            'media',  # Add this to prevent loops with media files
        ]

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip checks for exempt URLs
        if any(request.path.startswith(url) for url in self.exempt_urls):
            return None
            
        if not request.user.is_authenticated or request.user.is_superuser:
            return None
            
        try:
            profile = request.user.profile
            if not profile.is_complete():
                # Only redirect if we're not already going to profile page
                if request.resolver_match.url_name != 'business_profile':
                    return redirect('business_profile')
        except BusinessProfile.DoesNotExist:
            return redirect('business_profile')
        
        return None