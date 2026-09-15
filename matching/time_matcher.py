from datetime import datetime, date, time, timedelta

class TimeMatcher:
    """
    Evaluates temporal proximity between lost date/time and found date/time.
    Handles missing dates, times, same-day reports, cross-midnight cases, and invalid inputs.
    """

    def calculate_similarity(self, lost_item: dict, found_item: dict) -> float:
        """
        Calculates time similarity score (0.0 to 100.0).
        """
        lost_d = lost_item.get('lost_date')
        found_d = found_item.get('found_date')

        if not lost_d or not found_d:
            return 50.0  # Neutral fallback for missing date

        # Parse dates if string
        if isinstance(lost_d, str):
            try:
                lost_d = datetime.strptime(lost_d, '%Y-%m-%d').date()
            except ValueError:
                return 50.0

        if isinstance(found_d, str):
            try:
                found_d = datetime.strptime(found_d, '%Y-%m-%d').date()
            except ValueError:
                return 50.0

        lost_t = lost_item.get('lost_time') or time(12, 0)
        found_t = found_item.get('found_time') or time(12, 0)

        if isinstance(lost_t, str):
            try:
                lost_t = datetime.strptime(lost_t, '%H:%M:%S').time()
            except ValueError:
                try:
                    lost_t = datetime.strptime(lost_t, '%H:%M').time()
                except ValueError:
                    lost_t = time(12, 0)

        if isinstance(found_t, str):
            try:
                found_t = datetime.strptime(found_t, '%H:%M:%S').time()
            except ValueError:
                try:
                    found_t = datetime.strptime(found_t, '%H:%M').time()
                except ValueError:
                    found_t = time(12, 0)

        lost_dt = datetime.combine(lost_d, lost_t)
        found_dt = datetime.combine(found_d, found_t)

        # Difference in hours
        delta_hours = (found_dt - lost_dt).total_seconds() / 3600.0

        # Item found after it was lost (normal case)
        if 0 <= delta_hours <= 6:
            return 100.0
        elif 6 < delta_hours <= 24:
            return 90.0
        elif 24 < delta_hours <= 72:  # 1 to 3 days
            return 80.0
        elif 72 < delta_hours <= 168: # 3 to 7 days
            return 65.0
        elif 168 < delta_hours <= 720: # 1 to 4 weeks
            return 40.0
        elif delta_hours > 720:
            return 20.0
        else:
            # Found before lost (negative delta) - e.g. item found on 10th, user realizes lost on 12th
            abs_hours = abs(delta_hours)
            if abs_hours <= 24:
                return 80.0
            elif abs_hours <= 72:
                return 60.0
            elif abs_hours <= 168:
                return 40.0
            else:
                return 10.0
