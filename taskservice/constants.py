START_END_OFFSET = 360


class TIME_UNIT(object):
    SECOND = 's'
    MINUTE = 'm'
    HOUR = 'h'
    DAY = 'd'
    WEEK = 'w'
    MONTH = 'M'
    YEAR = 'y'

TIME_UNITS = {
    TIME_UNIT.SECOND: 'second',
    TIME_UNIT.MINUTE: 'minute',
    TIME_UNIT.HOUR: 'hour',
    TIME_UNIT.DAY: 'day',
    TIME_UNIT.WEEK: 'week',
    TIME_UNIT.MONTH: 'month',
    TIME_UNIT.YEAR: 'year'
}


class STATUS(object):
    NEW = 'n'
    IN_PROGRESS = 'ip'
    READY_FOR_REVIEW = 'rr'
    COMPLETED = 'c'
    SKIPPED = 's'

STATUS_LIST = {
    STATUS.NEW: 'New',
    STATUS.IN_PROGRESS: 'In Progress',
    STATUS.READY_FOR_REVIEW: 'Ready For Review',
    STATUS.COMPLETED: 'Completed',
    STATUS.SKIPPED: 'Skipped'
}


class SUPER_ROLE(object):
    OWNER = 10
    ADMIN = 5
    STANDARD = 0

SUPER_ROLES = {
    SUPER_ROLE.OWNER: 'Owner',
    SUPER_ROLE.ADMIN: 'Admin',
    SUPER_ROLE.STANDARD: 'Standard'
}


class ACCEPTANCE(object):
    ACCEPT = 'a'
    REJECT = 'r'
    WAITING = 'w'

ACCEPTANCES = {
    ACCEPTANCE.ACCEPT: 'Accept',
    ACCEPTANCE.REJECT: 'Reject',
    ACCEPTANCE.WAITING: 'Waiting',
}


class NODE_TYPE(object):
    START = 's'
    END = 'e'
    NORMAL = 'n'

NODE_TYPES = {
    NODE_TYPE.START: 'Start',
    NODE_TYPE.NORMAL: 'Normal',
    NODE_TYPE.END: 'End'
}
