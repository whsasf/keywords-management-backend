#!/usr/bin/env python3

from datetime import datetime
from datetime import timedelta
from datetime import timezone

def getBJTime():
    SHA_TZ = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    #return utc_now.astimezone(SHA_TZ)
    return utc_now