def format_time_allocation(minutes):
    if minutes >= 60:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} {'HOUR' if hours == 1 else 'HOURS'}"
        else:
            return f"{hours} {'HOUR' if hours == 1 else 'HOURS'} {remaining_minutes} MINUTES"
    else:
        return f"{minutes} MINUTES"