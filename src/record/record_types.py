# status values

from event import Event

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
