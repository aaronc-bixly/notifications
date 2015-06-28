def get_backend_id(backend_name):
    from notifications.models import NOTICE_MEDIA
    for bid, bname in NOTICE_MEDIA:
        if bname == backend_name:
            return bid
    return None
