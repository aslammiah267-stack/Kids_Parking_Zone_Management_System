from decimal import Decimal
from math import ceil

from .models import ParkingSettings


def calculate_parking_fee(duration_minutes, settings=None):
    """Reusable parking fee calculation used by exit, compiler, and reports.

    Default rule:
      first 30 minutes = 20 BDT
      every additional 30 minutes = 10 BDT
    """
    if duration_minutes is None:
        duration_minutes = 0
    duration_minutes = max(int(duration_minutes), 0)

    settings = settings or ParkingSettings.get_solo()
    first_minutes = int(settings.first_block_minutes)
    first_fee = Decimal(settings.first_block_fee)
    extra_minutes = int(settings.extra_block_minutes) or 1
    extra_fee = Decimal(settings.extra_block_fee)

    if duration_minutes <= first_minutes:
        return first_fee

    extra = duration_minutes - first_minutes
    extra_blocks = ceil(extra / extra_minutes)
    return first_fee + (Decimal(extra_blocks) * extra_fee)
