import traceback
import logging

from django.conf.global_settings import DEBUG
from services.notification import notify_trancaction_error

logger = logging.getLogger(__name__)

def handle_exception(e, notify_admin=True):
    error_message = str(e)
    traceback_details = traceback.format_exc()
    print(f"Exception occurred: {error_message}\nTraceback:\n{traceback_details}")
    logger.error(f"Exception occurred: {error_message}\nTraceback:\n{traceback_details}")
    if notify_admin and DEBUG is False:
        notify_trancaction_error(error_message, traceback_details)

