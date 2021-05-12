import importlib
import os
import sys


def RequestExposerMiddleware(get_response):
    def middleware(request):
        dirname = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        settings = importlib.import_module(f"{dirname}.settings")
        pretty_printing = importlib.import_module(f"{dirname}.pretty_printing")
        dumps = pretty_printing.dumps
        import logging
        logger = logging.getLogger()
        #logger.info(dumps(request))

#        import os
#
#        dirname = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#        settings_path = f"{dirname}.settings"
#
#        print(settings_path)
#        print(settings_path)
#
#        from django.utils.module_loading import import_string
#        settings = import_string(settings_path)
#        print(settings)

        #from django.utils.module_loading import import_string
        #ValidationError = import_string('django.core.exceptions.ValidationError')
        #is equivalent to:
        #from django.core.exceptions import ValidationError

        #import json
        #print(json.dumps(sys.path,default=str,indent=4))
        
        import pytz
        import datetime
        dt = datetime.datetime.utcnow()
        current_time_utc = pytz.utc.localize(dt)
        tzinfo = pytz.timezone('Asia/Kolkata')
        current_time_time_zone = current_time_utc.astimezone(tzinfo)

        try:
            s = current_time_time_zone.isoformat(timespec='milliseconds')
        except TypeError:
            s = current_time_time_zone.isoformat()


        url = request.build_absolute_uri()
        method = request.method
        current_time = datetime.datetime.utcnow()
        ref = request.META.get("HTTP_REFERER", "HTTP_REFERER_NONE")
        if ref == "HTTP_REFERER_NONE":
            ref = request.META.get("HTTP_HOST", "HTTP_HOST_NONE")+request.META.get("REQUEST_URI", "REQUEST_URI_NONE")

        tag = f"{s}_{method}_{url}__referer:{ref}"

        print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<{tag}")
        settings.exposed_request.append(tag)

        response = get_response(request)

        settings.exposed_request.remove(tag)
        print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>{tag}")

        return response

    return middleware