def event_listener(event):
    if event.exception:
        print('Job failed')