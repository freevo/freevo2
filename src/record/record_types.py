# status values

MISSED    = 'missed'
SAVED     = 'saved'
SCHEDULED = 'scheduled'
RECORDING = 'recording'
CONFLICT  = 'conflict'
DELETED   = 'deleted'
FAILED    = 'failed'

# Time when to schedule the recording on a recorder
# (only next hour, update every 30 minutes)
SCHEDULE_TIMER = 60 * 60

# multicast url for live tv
LIVETV_URL = '224.224.224.10'

# Stuff from freevo config
from config import TV_RECORD_START_PADDING, TV_RECORD_STOP_PADDING, \
     TV_RECORD_FILEMASK, TV_RECORD_DIR
