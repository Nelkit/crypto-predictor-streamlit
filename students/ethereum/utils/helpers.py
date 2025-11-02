from dateutil import parser
import pandas as pd

def format_currency_short(value: float) -> str:
    """
    Format large currency values into a compact human-readable form.
    Examples:
        1500 -> $1.5K
        1250000 -> $1.25M
        470114180844 -> $470.11B
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        return "N/A"

    # Handle very small or invalid values
    if abs(num) < 1_000:
        return f"${num:,.2f}"

    # Define suffixes
    for unit in ["", "K", "M", "B", "T"]:
        if abs(num) < 1000.0:
            return f"{num:,.2f}{unit}"
        num /= 1000.0
    return f"{num:,.2f}P"  # For anything beyond trillions

def format_iso_date(date: str) -> str:
    """
    Formats an ISO date string to a date in ISO format (YYYY-MM-DD).

    Args:
        date (str): The ISO date string to format.

    Returns:
        str: The formatted date string in ISO format, or an error message if parsing fails.
    """
    try:
        dt_parser = parser.isoparse(date)
        date_formatted = dt_parser.date().isoformat()
    except ValueError:
        date_formatted = "⚠️ Could not parse last update date."

    return date_formatted

def format_datetime(date: str) -> str:
    """
    Formats a date value to a human-readable string in "Mon DD, YYYY HH:MM" format.

    Args:
        date (str, int, float, pd.Timestamp): The date to format. If int/float, treated as Unix timestamp in seconds.

    Returns:
        str: The formatted date string, or "Unknown date" if the type is not recognized.
    """
    if isinstance(date, (int, float)):
        date_str = pd.to_datetime(date, unit="s").strftime("%b %d, %Y %H:%M")
    elif isinstance(date, pd.Timestamp):
        date_str = date.strftime("%b %d, %Y %H:%M")
    else:
        date_str = "Unknown date"
    return date_str