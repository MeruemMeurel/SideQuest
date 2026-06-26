from rest_framework.negotiation import DefaultContentNegotiation


class APIJSONContentNegotiation(DefaultContentNegotiation):
    def select_renderer(self, request, renderers, format_suffix=None):
        if request.path.startswith("/api/v1/"):
            for renderer in renderers:
                if renderer.format == "json":
                    return renderer, renderer.media_type

        return super().select_renderer(request, renderers, format_suffix)
