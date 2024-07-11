from datetime import timedelta
from enum import Enum
from typing import Callable
import i18n
class Granularity(Enum):
    DAYS = "days"
    MINUTES="minutes"
    WEEKS = "weeks"

class TimeUnit(Enum):
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"
    SECOND = "second"

def format_timedelta(
    delta: timedelta,
    lang: str,
    add_direction: bool = True,
    granularity: Granularity = Granularity.DAYS,
    translate: Callable[[str], str] = i18n.t
) -> str:
    """
    Format a timedelta object into a human-readable string.

    Args:
        delta: The timedelta object representing the time difference.
        lang: The language locale (used for potential future localization).
        add_direction: Whether to add directional indicators (e.g., "in", "ago").
        granularity: The level of detail for formatting.
        translate: Function to translate strings (default is identity function).

    Returns:
        The formatted timedelta string.

    Raises:
        ValueError: If an invalid granularity is provided.
    """
    days = delta.days
    is_future = delta.total_seconds() > 0

    if granularity == Granularity.DAYS:
        return _format_days(delta, days, is_future, add_direction, translate)
    elif granularity == Granularity.MINUTES:  # Add this block
        return _format_minutes(delta, is_future, add_direction, translate)
    elif granularity == Granularity.WEEKS:
        return _format_weeks(delta, days, is_future, add_direction, translate)
    else:
        raise ValueError(f"Unsupported granularity: {granularity}")
def _format_minutes(
    delta: timedelta,
    total_minutes: int,
    is_future: bool,
    add_direction: bool,
    translate: Callable[[str], str]
) -> str:
    """Format timedelta in minutes."""
    abs_minutes = abs(total_minutes)
    if abs_minutes < 60:
        return _format_timedelta_detailed(delta, TimeUnit.MINUTE, 1, add_direction, translate)
    elif abs_minutes < 1440:  # Less than a day
        return _format_timedelta_detailed(delta, TimeUnit.HOUR, 1, add_direction, translate)
    else:
        return _format_days(delta, delta.days, is_future, add_direction, translate)

def _format_days(
    delta: timedelta,
    days: int,
    is_future: bool,
    add_direction: bool,
    translate: Callable[[str], str]
) -> str:
    """Format timedelta in days."""
    if days == 0:
        return translate("Today")
    elif abs(days) < 7 or abs(days) >= 60:
        return _format_timedelta_detailed(delta, TimeUnit.DAY, 1, add_direction, translate)
    else:
        return _format_timedelta_detailed(delta, TimeUnit.DAY, 10, add_direction, translate)

def _format_weeks(
    delta: timedelta,
    days: int,
    is_future: bool,
    add_direction: bool,
    translate: Callable[[str], str]
) -> str:
    """Format timedelta in weeks."""
    weeks = abs(days) // 7
    result = translate("1 week") if weeks == 1 else translate(f"{weeks} weeks")
    
    if add_direction:
        return _add_direction(result, is_future, translate)
    return result

def _format_timedelta_detailed(
    delta: timedelta,
    unit: TimeUnit,
    threshold: int,
    add_direction: bool,
    translate: Callable[[str], str]
) -> str:
    """Format timedelta with detailed units."""
    is_future = delta.total_seconds() > 0
    delta = abs(delta)
    
    days, hours, minutes, seconds = _break_down_delta(delta)

    value, unit_str = _select_appropriate_unit(days, hours, minutes, seconds, unit, threshold)

    result = f"{value} {translate(unit_str)}"

    if add_direction:
        return _add_direction(result, is_future, translate)
    return result

def _break_down_delta(delta: timedelta) -> tuple[int, int, int, int]:
    """Break down a timedelta into days, hours, minutes, and seconds."""
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return days, hours, minutes, seconds

def _select_appropriate_unit(
    days: int,
    hours: int,
    minutes: int,
    seconds: int,
    unit: TimeUnit,
    threshold: int
) -> tuple[int, str]:
    """Select the appropriate unit based on the timedelta breakdown."""
    if unit == TimeUnit.DAY or (days >= threshold and unit == TimeUnit.HOUR):
        return days, "day" if days == 1 else "days"
    elif unit == TimeUnit.HOUR or hours >= threshold:
        total_hours = hours + (days * 24)
        return total_hours, "hour" if total_hours == 1 else "hours"
    elif unit == TimeUnit.MINUTE or minutes >= threshold:
        total_minutes = minutes + (hours * 60) + (days * 24 * 60)
        return total_minutes, "minute" if total_minutes == 1 else "minutes"
    else:
        total_seconds = seconds + (minutes * 60) + (hours * 3600) + (days * 24 * 3600)
        return total_seconds, "second" if total_seconds == 1 else "seconds"

def _add_direction(result: str, is_future: bool, translate: Callable[[str], str]) -> str:
    """Add direction (future or past) to the result string."""
    return translate("in {0}").format(result) if is_future else translate("{0} ago").format(result)

# Example usage
if __name__ == "__main__":
    from datetime import datetime

    def mock_translate(text: str) -> str:
        """Mock translation function."""
        return text

    now = datetime.now()
    past_date = now - timedelta(days=5, hours=3)
    future_date = now + timedelta(days=2, hours=12)

    print(format_timedelta(now - past_date, "en", granularity=Granularity.DAYS, translate=mock_translate))
    print(format_timedelta(now-future_date , "en", granularity=Granularity.DAYS, translate=mock_translate))
    print(format_timedelta(now - now, "en", granularity=Granularity.WEEKS, translate=mock_translate))
    print(format_timedelta(future_date - now, "en", granularity=Granularity.WEEKS, translate=mock_translate))