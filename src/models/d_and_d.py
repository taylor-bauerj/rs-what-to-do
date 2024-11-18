from datetime import datetime, timedelta
import pytz

class TimedActivity:
    def __init__(self, name, reset_period, requirements=None):
        self.name = name
        self.reset_period = reset_period
        self.requirements = requirements or {}
        self.last_completed = {}  # Dictionary to store completion time per user
        
    def is_available(self, user_id, tracker):
        if user_id not in self.last_completed:
            return True
            
        now = datetime.now(pytz.UTC)
        last_completion = self.last_completed[user_id]
        next_reset = self._get_next_reset(last_completion)
            
        return now >= next_reset
    
    def _get_next_reset(self, completion_time):
        if self.reset_period == 'daily':
            # Next UTC midnight
            next_reset = completion_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif self.reset_period == 'weekly':
            # Next Wednesday UTC midnight
            days_until_wednesday = (2 - completion_time.weekday()) % 7
            next_reset = completion_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_until_wednesday)
        else:  # monthly
            # First day of next month UTC midnight
            if completion_time.month == 12:
                next_reset = completion_time.replace(year=completion_time.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                next_reset = completion_time.replace(month=completion_time.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return next_reset

    def mark_completed(self, user_id, tracker):
        tracker.mark_completed(self.name, user_id)
