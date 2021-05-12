# PLACE ONLY COMMON SETTINGS HERE

import os
import logging
import traceback
import json
import sys

## this helps to debug things easily
#https://github.com/alexmojaki/snoop
import snoop

def path(event):
    return event.code.co_filename[-20:]

#But instead of [-20:] add your own logic to trim the starting folder.

snoop.install(enabled=False,columns=[path, "function"])



PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PYTHON_PATH = sys.executable
VENV_PATH = os.path.dirname(os.path.dirname(PYTHON_PATH))


# for django ORM to work in jupyter
# https://stackoverflow.com/a/62119475
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# During launch jupyter notebook server will show the address and port and token
# that you will need to use as URL to access it.

NOTEBOOK_ARGUMENTS = [
    '--ip', '0.0.0.0',
    '--port', '8888'
]

#######################################################
# Logging objects, sql, traceback and strings
#######################################################

import logging
import traceback

from datetime import datetime
from pytz import timezone

exposed_request=[]
print(f"exposed_request = [] :: {exposed_request}")

class TimeFormatter(logging.Formatter):
    """override logging.Formatter to use an aware datetime object"""
    def converter(self, timestamp):
        #dt = datetime.datetime.fromtimestamp(timestamp)
        #we use
        import pytz
        import datetime
        dt = datetime.datetime.utcnow()
        current_time_utc = pytz.utc.localize(dt)
        tzinfo = pytz.timezone('Asia/Kolkata')
        current_time_time_zone = current_time_utc.astimezone(tzinfo)
        return current_time_time_zone
        
    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s


# Verbose formatter to be used for the handler used in logging "custom_string"
class VerFormatter(TimeFormatter):
    def format(self, record):
        ## We want to show some code lines while logging. So that its eays to know 
        #create a list of all the linenumber: lines 
        lines=[]
        string = ""
        file = record.pathname
        line = record.lineno
        if os.path.exists(file):
            line -= 1
            with open(file,"r") as f:
                rl = f.readlines()
                tblines = rl[max(line-5,0):min(line+3,len(rl))]
                # read 2 lines before and 2 lines after
                for i,tl in enumerate(tblines):
                    tl = tl.rstrip()

                    if i==5:
                        string = string + " =====> "+str(line+1+i-5)+":  "+tl+" <====\n"
                    elif tl:
                        string = string + "        "+str(line+1+i-5)+":  "+tl+"\n"


        # colorize the code
        import pygments
        from pygments.lexers.python import Python3Lexer
        from pygments.formatters import TerminalTrueColorFormatter
        # windows terminal has no colors
        #code = pygments.highlight(
        #    code,
        #    Python3Lexer(),
        #    #TerminalTrueColorFormatter(style='monokai') #use for terminal
        #    TerminalTrueColorFormatter() #use for jupyter notebook
        #)

        #add new attributes to record which will be used later
        # we also want to have the url requested and its method
        record.absolute_path = json.dumps(exposed_request,default=str,indent=4)
        record.codelines = string
        record.topline = "--------------------------------------------------------------------------------------------------------------"
        record.botline = "--------------------------------------------------------------------------------------------------------------"
        return super(VerFormatter, self).format(record)

class RequestLoggingNotUrllib(TimeFormatter):
    def format(self, record):
        #add new attributes to record which will be used later
        # we also want to have the url requested and its method
        #record.absolute_path = json.dumps(exposed_request,default=str,indent=4)
        record.absolute_path = exposed_request
        record.topline = "--------------------------------------------------------------------------------------------------------------"
        record.botline = "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        return super(RequestLoggingNotUrllib, self).format(record)



# this is for getting request urllib logs
def print_to_log(*args):
    logging.getLogger("urllib3").debug(" ".join(args))

import http.client as http_client
http_client.HTTPConnection.debuglevel = 1
http_client.print = print_to_log


class RequestsUrlLibFormatter(TimeFormatter):
    def format(self, record):
        #add new attributes to record which will be used later
        # we also want to have the url requested and its method
        #record.absolute_path = json.dumps(exposed_request,default=str,indent=4)


        if record.msg.startswith("Starting new HTTPS connection"):
            import traceback
            import re
            tracearray = traceback.extract_stack()
            
            filepath = PROJECT_PATH
            filepath_dont = VENV_PATH
            filepath1 = f"{VENV_PATH}/lib/python3.7/site-packages/rest_auth/"
            filepath2 = f"{VENV_PATH}/lib/python3.7/site-packages/allauth/"
            filepath3 = f"{VENV_PATH}/lib/python3.7/site-packages/django/contrib/auth/"

            #print(f"filepath: {filepath}")
            #print(f"filepath_dont: {filepath_dont}")
            #print(f"filepath1: {filepath1}")
            #print(f"filepath2: {filepath2}")
            #print(f"filepath3: {filepath3}")

    #        #matches = [i for i in tracearray if (re.search(rf"{filepath}", i) and not re.search(rf"{filepath_dont}", i)) ]
    #        for i in range(0,len(tracearray)):
    #            if (re.search(rf"{filepath}", tracearray[i]) or re.search(rf"{filepath1}", tracearray[i]) or re.search(rf"{filepath2}", tracearray[i])):
    #                tracearray[i] = f"{i}***{tracearray[i]}"
    #            else:
    #                tracearray[i] = f"{i}{tracearray[i]}"


            matches2 = [i for i in tracearray 
                        if (i[0].startswith(filepath) and not i[0].startswith(filepath_dont))
                            or i[0].startswith(filepath1) 
                            or i[0].startswith(filepath2) 
                            or i[0].startswith(filepath3) 
                        ]


            matches=[]
            for file,line,w1,w2 in matches2[2:-1]:
                string = ""
                if re.search(rf"{filepath}", file):
                    string = string + '\n***************************************************************\n->File "{}", line {}, in {}\n'.format(file,line,w1)
                else:
                    string = string + '->File "{}", line {}, in {}\n'.format(file,line,w1)


                

                if os.path.exists(file):
                    line -= 1
                    with open(file,"r") as f:
                        rl = f.readlines()
                        tblines = rl[max(line-5,0):min(line+3,len(rl))]
                        # read 2 lines before and 2 lines after
                        for i,tl in enumerate(tblines):
                            tl = tl.rstrip()
                            if i==5:
                                string = string + " =====> "+str(line+1+i-5)+":  "+tl+" <====\n"
                            elif tl:
                                string = string + "        "+str(line+1+i-5)+":  "+tl+"\n"
                matches.append(string)

            traceback_matches = ''.join(matches)
            record.above = "\n--------------------------------------------------------------------------------------------------------------\n"+str(exposed_request)+"\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"+traceback_matches+"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"

        else:
            record.above = ""




        return super(RequestsUrlLibFormatter, self).format(record)


# SQL formatter to be used for the handler used in logging "django.db.backends"
class SQLFormatter(TimeFormatter):
    local_request = None
    def format(self, record):

        # Check if Pygments is available for coloring 
        try:
            import pygments
            from pygments.lexers import SqlLexer
            from pygments.formatters import TerminalTrueColorFormatter
        except ImportError:
            pygments = None

        # Check if sqlparse is available for indentation
        try:
            import sqlparse
        except ImportError:
            sqlparse = None

        # Remove leading and trailing whitespaces
        sql = record.sql.strip()

        if sqlparse:
            # Indent the SQL query
            sql = sqlparse.format(sql, reindent=True)

        import traceback
        import re
        tracearray = traceback.extract_stack()

        filepath = PROJECT_PATH
        filepath_dont = VENV_PATH
        filepath1 = f"{VENV_PATH}/lib/python3.7/site-packages/rest_auth/"
        filepath2 = f"{VENV_PATH}/lib/python3.7/site-packages/allauth/"
        filepath3 = f"{VENV_PATH}/lib/python3.7/site-packages/django/contrib/auth/"
        filepath4 = f"{VENV_PATH}/lib/python3.7/site-packages/rest_framework"
        filepath5 = f"{VENV_PATH}/lib/python3.7/site-packages/knox"
        
        #print(f"filepath: {filepath}")
        #print(f"filepath_dont: {filepath_dont}")
        #print(f"filepath1: {filepath1}")
        #print(f"filepath2: {filepath2}")
        #print(f"filepath3: {filepath3}")

#        #matches = [i for i in tracearray if (re.search(rf"{filepath}", i) and not re.search(rf"{filepath_dont}", i)) ]
#        for i in range(0,len(tracearray)):
#            if (re.search(rf"{filepath}", tracearray[i]) or re.search(rf"{filepath1}", tracearray[i]) or re.search(rf"{filepath2}", tracearray[i])):
#                tracearray[i] = f"{i}***{tracearray[i]}"
#            else:
#                tracearray[i] = f"{i}{tracearray[i]}"

        matches2 = [i for i in tracearray 
                    if (i[0].startswith(filepath) and not i[0].startswith(filepath_dont))
                        or i[0].startswith(filepath1) 
                        or i[0].startswith(filepath2) 
                        or i[0].startswith(filepath3) 
                        or i[0].startswith(filepath4) 
                        or i[0].startswith(filepath5)
                    ]
        #matches2 = tracearray

        matches=[]
        for file,line,w1,w2 in matches2[2:-1]:
            string = ""
            if re.search(rf"{filepath}", file):
                string = string + '\n***************************************************************\n->File "{}", line {}, in {}\n'.format(file,line,w1)
            else:
                string = string + '->File "{}", line {}, in {}\n'.format(file,line,w1)


            if os.path.exists(file):
                line -= 1
                with open(file,"r") as f:
                    rl = f.readlines()
                    tblines = rl[max(line-5,0):min(line+3,len(rl))]
                    # read 2 lines before and 2 lines after
                    for i,tl in enumerate(tblines):
                        tl = tl.rstrip()

                        if i==5:
                            string = string + " =====> "+str(line+1+i-5)+":  "+tl+" <====\n"
                        elif tl:
                            string = string + "        "+str(line+1+i-5)+":  "+tl+"\n"
            matches.append(string)


        record.traceback = ''.join(matches)


        # Set the record's statement to the formatted query
        record.statement = sql
        if 'duration' in record.__dict__:
          pass
        else:
          record.duration = "NA"

        #record.absolute_path = json.dumps(exposed_request,default=str,indent=4)
        record.absolute_path = exposed_request
        record.topline = "--------------------------------------------------------------------------------------------------------------"
        record.botline = "--------------------------------------------------------------------------------------------------------------"

        return super(SQLFormatter, self).format(record)

### Change this to closed when there are too many queries going on.and use 
### logger_database.filters[0].open() INDSIDE THE views function not on the top
LoggerGate_Default_State="open"  # use this if we want to see all the sql
#LoggerGate_Default_State="closed"  # use this if we want dont want to see all the sql


# Filter class to stop or start logging for "django.db.backends"
class LoggerGate:
    def __init__(self, state=LoggerGate_Default_State):
        # We found that the settings.py runs twice and the filters are created twice. So we have to keep only one. So we delete all the previous filters before we create the new one
        import logging
        logger_database = logging.getLogger("django.db.backends")
        try:
            for filter in logger_database.filters:
                logger_database.removeFilter(filter)
        except Exception as e:
            pass
        self.state = state

    def open(self):
        self.state = 'open'

    def close(self):
        self.state = 'closed'

    def filter(self, record):
        """
        Determine if the specified record is to be logged.

        Is the specified record to be logged? Returns 0/False for no, nonzero/True for
        yes. If deemed appropriate, the record may be modified in-place.
        """
        return self.state == 'open'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'sql': {
            '()': SQLFormatter,
            'format': '%(topline)s\n%(asctime)s\nXXX%(levelname)sXXX %(funcName)s() %(pathname)s[:%(lineno)s] %(name)s\n%(absolute_path)s\n%(topline)s\n%(traceback)s\n\n\n[%(duration).3f]\n%(statement)s\n%(botline)s\n',
            #'format': '%(topline)s\n%(asctime)s:::::::::SQL:::::::::::%(levelname)-1s\n%(botline)s\n%(traceback)s\n\n\n[%(duration).3f]\n%(statement)s\n%(botline)s\n',
        },
        'verbose': {
            '()': VerFormatter,
            'format': '%(topline)s\n%(asctime)s\nXXX%(levelname)sXXX %(funcName)s() %(pathname)s[:%(lineno)s] %(name)s\n%(absolute_path)s\n%(topline)s\n\n%(codelines)s\n\n%(message)s\n\n%(codelines)s',
            #'datefmt': "[%d/%b/%Y %H:%M:%S %p %Z]"
        },
        'requestLoggingNotUrllib': {
            '()': RequestLoggingNotUrllib,
            'format': '%(topline)s\n%(asctime)s--XXX%(levelname)sXXX %(funcName)s() %(pathname)s[:%(lineno)s] %(name)s\n%(absolute_path)s\n%(botline)s\n%(message)s\n%(botline)s\n',
            #'datefmt': "[%d/%b/%Y %H:%M:%S %p %Z]"
        },
        'verbose_urllib': {
            '()': RequestsUrlLibFormatter,
            'format': '%(above)s%(asctime)s::%(levelname)-0s::%(message)s',
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{asctime}] {message}\n\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n############################################################################################\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))\n(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&\n',
            'datefmt' : '%Y-%m-%d %H:%M:%S',
            'style': '{',
            }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
        },
        'console_requestLoggingNotUrllib': {
            'level': 'DEBUG',
            'formatter': 'requestLoggingNotUrllib',
            'class': 'logging.StreamHandler',
        },
        'console_urllib': {
            'level': 'DEBUG',
            'formatter': 'verbose_urllib',
            'class': 'logging.StreamHandler',
        },
        'sql': {
            'class': 'logging.StreamHandler',
            'formatter': 'sql',
            'level': 'DEBUG',
        },
        'django.server': {
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
    },
    'filters': {
        'myfilter': {
            '()': LoggerGate,
        }
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['sql'],
            'level': 'DEBUG',
            'propagate': False,
            'filters': ['myfilter']
        },
#        'django.db.backends.schema': {
#            'handlers': ['console'],
#            'level': 'DEBUG',
#            'propagate': False,
#        },
        '': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.server':{
            'handlers': ['django.server'],
            'propagate': False,
        },
        # added from django-request-logging
        'django.request': {
            'handlers': ['console_requestLoggingNotUrllib'],
            'level': logging.CRITICAL if DEBUG else 'INFO',  # change debug level as appropiate
            'propagate': False,
        },
        # added from django-request-logging
        'urllib3': {
            'handlers': ['console_urllib'],
            'level': 'DEBUG',  # change debug level as appropiate
            'propagate': False,
        },
        # https://stackoverflow.com/a/60503706/2897115
        'asyncio': {
            'level': 'WARNING',
        },
    }
}

# added from django-LoggingMiddleware
REQUEST_LOGGING_DATA_LOG_LEVEL=logging.CRITICAL
REQUEST_LOGGING_HTTP_4XX_LOG_LEVEL=logging.CRITICAL
REQUEST_LOGGING_MAX_BODY_LENGTH = 1000