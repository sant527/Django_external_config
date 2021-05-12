## COPY PASTE THESE FROM settings.py
INSTALLED_APPS = [

]

MIDDLEWARE = [

]


# DONT TOUCH THESE
INSTALLED_APPS =+ ['django_extensions']

# basename
dirname = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MIDDLEWARE = MIDDLEWARE + [
    f"{dirname}.external_config.custom_middleware.request_exposure.RequestExposerMiddleware", #<--- will set the exposed_request  variable, initiall define it as None
    f"{dirname}.external_config.custom_middleware.request_logging.middleware.LoggingMiddleware", #<--- Added install djang-request-logging
]