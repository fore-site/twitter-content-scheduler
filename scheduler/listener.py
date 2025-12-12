import logging

logger = logging.getLogger()
file_logger = logging.getLogger('fileLogger')

def event_listener(event):
    if event.exception:
        file_logger.exception(f"Job {event.job_id} raised {event.exception}")
    else:
        logger.info('Job successfully executed.')