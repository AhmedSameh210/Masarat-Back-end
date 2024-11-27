# users/management/commands/show_urls.py
from django.core.management.base import BaseCommand
from django.urls import get_resolver, URLPattern, URLResolver

class Command(BaseCommand):
    help = 'Displays all the registered URLs in the project'

    def handle(self, *args, **kwargs):
        # Get the root URL patterns
        url_patterns = get_resolver().url_patterns
        
        # Recursively print all the URL patterns
        self.print_url_patterns(url_patterns)

    def print_url_patterns(self, patterns, prefix=''):
        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                # If it's a URLPattern (endpoint), print it
                self.stdout.write(f'{prefix}{pattern.pattern}')
            elif isinstance(pattern, URLResolver):
                # If it's a URLResolver (nested pattern), recurse
                self.print_url_patterns(pattern.url_patterns, prefix=f'{prefix}{pattern.pattern}/')
