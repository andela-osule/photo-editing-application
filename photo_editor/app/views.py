from django.shortcuts import render
from django.views.generic import View


class RootFilesView(View):
    """Renders requests for `sitemap.xml`, `robots.txt` and `humans.txt`"""

    def get(self, request, *args, **kwargs):
        """Returns response for `GET` request to the website root"""
        filename = self.kwargs.get('filename')
        return render(
            request, filename,
            {'page_title': filename}, content_type="text/plain"
        )

    