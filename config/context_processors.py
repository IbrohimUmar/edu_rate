from django.core.cache import cache
from .settings import UNIVERSITY_NAME, UNIVERSITY_SHORT_NAME, PROJECT_NAME

def config_context(request):
    config = cache.get("site_config")
    if not config:
        data = {
            "UNIVERSITY_NAME":UNIVERSITY_NAME,
            "PROJECT_NAME":PROJECT_NAME,
                "UNIVERSITY_SHORT_NAME":UNIVERSITY_SHORT_NAME}

        cache.set("site_config", data, 60 * 60)  # 1 soat cache
    return {"site_config": config}
