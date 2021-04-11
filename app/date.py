from datetime import date, datetime, timedelta

CURRENT_MONTH = datetime.now().replace(day=1).strftime("%Y-%m-%d")


def get_available_months(starting_month=date(2020, 1, 1)):
    """Get a list of all the months from starting_month to the current date.

    This returns a list of date objects for each valid month.
    """

    now = datetime.now().date()
    diff = now - starting_month

    all_days = [starting_month + timedelta(days=i) for i in range(diff.days)]
    month_trunc = [date.replace(day=1) for date in all_days]
    unique_months = list(set(month_trunc))
    ordered_months = sorted(unique_months, reverse=True)

    return ordered_months
