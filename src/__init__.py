# -*- coding: utf-8 -*-
"""src Module"""
from datetime import datetime
import logging
import re
from zoneinfo import ZoneInfo

from src.utils import get_package_version

__all__ = ["LocalTimeFormatter"]

PROGRAM_NAME: str = 'SaliencyMapDemo'
__version__ = get_package_version()


class LocalTimeFormatter(logging.Formatter):
    """
    ログの時刻表示を指定したタイムゾーンに変換するクラス。
    """
    time_zone: str = "GMT"
    pattern = re.compile(r"([\.|,]\%\d{1,}f)(\%z)?", re.IGNORECASE)
    """
    %Y-%m-%dT%H:%M:%S.%03f
    %Y-%m-%dT%H:%M:%S.%03f%z
    """
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(
            record.created,
            ZoneInfo(self.time_zone)
        )

        if datefmt is None:
            s = dt.strftime(self.default_time_format)
            return s

        t = dt.strftime(re.sub(self.pattern, "", datefmt))
        match = re.search(self.pattern, datefmt)
        if match is None:
            return t

        groups = match.groups()
        msec_format = groups[0] if groups[0] else ""
        time_zone_format = groups[1] if groups[1] else ""
        time_zone_str = dt.strftime(time_zone_format)
        msec_format = msec_format.replace("f", "d")
        s = f"{t}{msec_format % record.msecs }{time_zone_str}"
        return s
