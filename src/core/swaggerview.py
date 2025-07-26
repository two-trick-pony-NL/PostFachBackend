from drf_spectacular.views import SpectacularSwaggerView

class CustomSwaggerView(SpectacularSwaggerView):
    def get_extra_settings(self):
        extra = super().get_extra_settings() or {}
        extra['securityDefinitions'] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
        extra['security'] = [{"BearerAuth": []}]
        return extra
