#!/usr/bin/python

# -*- coding: utf-8 -*-

# type: ignore

"""
Find the next calendar events with Chime details

Python 2 for portability. Needs "brew install ical-buddy".
"""

import re
import subprocess  # nosec
import sys
import time
from collections import OrderedDict
import datetime

from workflow import Workflow3


class JoinableEvent(object):
    """Represent an event Alfred can join."""

    def __init__(self, event_name, start_time, end_time, sort_time):
        self.event_name = re.sub(
            r"""(
                (fw|re|):
                |
                \[external\]
                |
                invitation:
                |
                \([a-z0-9_+-]+@[a-z0-9.-]+\)  # email address
                )""",
            "",
            event_name,
            flags=re.IGNORECASE | re.VERBOSE,
        ).strip()
        self.start_time = start_time
        self.end_time = end_time
        self.sort_time = sort_time
        if self.sort_time:
            self.start_datetime = datetime.datetime.strptime(
                self.sort_time, "%H:%M"
            ).time()
        else:
            self.start_datetime = None

    def description(self):
        raise NotImplementedError

    def url(self):
        raise NotImplementedError

    def icon(self):
        raise NotImplementedError

    def time_field(self):
        now = datetime.datetime.now().time()
        try:
            if self.start_datetime:
                if self.start_datetime < now:
                    return "ending at {}".format(self.end_time)
        except Exception:
            pass
        return "starting at {}".format(self.start_time)


class ChimeEvent(JoinableEvent):
    """Represent a Chime event."""

    def __init__(
        self, event_name, start_time, end_time, sort_time, meeting_id, meeting_pin
    ):
        super(ChimeEvent, self).__init__(event_name, start_time, end_time, sort_time)
        self.meeting_id = meeting_id
        self.meeting_pin = meeting_pin

    def description(self):
        if self.meeting_id is not None:
            return "Join meeting {} with Chime ID {}".format(
                self.time_field(), self.meeting_id
            )
        else:
            return "Join meeting {} with Chime PIN {}".format(
                self.time_field(), self.meeting_pin
            )

    def url(self):
        if self.meeting_pin is not None:
            return "chime://meeting?pin={}".format(self.meeting_pin)
        else:
            return "chime://meeting?pin={}".format(self.meeting_id)

    def icon(self):
        return None  # default icon from Alfred

    def __repr__(self):
        return "chime: {} {}-{} ({}) id:{} pin:{}".format(
            self.event_name,
            self.start_time,
            self.end_time,
            self.sort_time,
            self.meeting_id,
            self.meeting_pin,
        )


class BroadcastEvent(JoinableEvent):
    """Represent a Broadcast event."""

    def __init__(self, event_name, start_time, end_time, sort_time, broadcast_url):
        super(BroadcastEvent, self).__init__(
            event_name, start_time, end_time, sort_time
        )
        self.broadcast_url = broadcast_url

    def description(self):
        return "Open Broadcast live event {}".format(self.time_field())

    def url(self):
        return self.broadcast_url

    def icon(self):
        return "broadcast.png"


class TeamsEvent(JoinableEvent):
    """Represent a Teams event."""

    def __init__(self, event_name, start_time, end_time, sort_time, teams_url):
        super(TeamsEvent, self).__init__(event_name, start_time, end_time, sort_time)
        self.teams_url = teams_url

    def description(self):
        return "Join Teams meeting {}".format(self.time_field())

    def url(self):
        return self.teams_url

    def icon(self):
        return "teams.png"


class MeetEvent(JoinableEvent):
    """Represent a Google Meet event."""

    def __init__(self, event_name, start_time, end_time, sort_time, meet_url):
        super(MeetEvent, self).__init__(event_name, start_time, end_time, sort_time)
        if "@" in self.event_name:
            self.event_name = self.event_name.split("@")[0]
        self.meet_url = meet_url

    def description(self):
        return "Join Google Meet meeting {}".format(self.time_field())

    def url(self):
        return self.meet_url

    def icon(self):
        return "meet.png"


class CalendarScanner(object):
    def __init__(self):
        self.event_name = None
        self.input_filename = None
        self.events = {}
        self._reset()

    def _reset(self):
        self.meeting_pin = None
        self.meeting_id = None
        self.start_time = None
        self.end_time = None
        self.sort_time = None
        self.broadcast_url = None
        self.teams_url = None
        self.meet_url = None

    def _save(self):
        if not self.event_name:
            raise RuntimeError("Bad event data")
        if self.meeting_id or self.meeting_pin:
            return ChimeEvent(
                self.event_name,
                self.start_time,
                self.end_time,
                self.sort_time,
                self.meeting_id,
                self.meeting_pin,
            )
        if self.broadcast_url:
            return BroadcastEvent(
                self.event_name,
                self.start_time,
                self.end_time,
                self.sort_time,
                self.broadcast_url,
            )
        if self.teams_url:
            return TeamsEvent(
                self.event_name,
                self.start_time,
                self.end_time,
                self.sort_time,
                self.teams_url,
            )
        if self.meet_url:
            return MeetEvent(
                self.event_name,
                self.start_time,
                self.end_time,
                self.sort_time,
                self.meet_url,
            )
        raise RuntimeError("Bad event data")

    @staticmethod
    def _first_valid_item(*args):
        for item in args:
            if item is not None:
                return item
        return None

    def get_events(self, wf):
        if self.input_filename:
            # for testing
            with open(self.input_filename, "r") as fh:
                output = fh.read().decode("utf-8")
        else:
            try:
                _output = subprocess.check_output(  # nosec
                    [
                        "/Users/thulsimo/.homebrew/bin/icalBuddy",
                        "-b",
                        "__start ",  # event "bullet" style
                        "-n",  # omit events earlier than now
                        "-ea",  # exclude all-day events
                        "eventsToday",
                    ]
                )
            except OSError:
                wf.warn_empty("Please 'brew install ical-buddy'")
                wf.send_feedback()
                return
            except subprocess.CalledProcessError:
                wf.warn_empty(
                    "Error running icalBuddy; maybe no Calendar access granted in macOS?"
                )
                wf.send_feedback()
                return
            output = _output.decode(encoding="utf-8")

        events = {}

        for line in output.splitlines():
            line = line.rstrip()
            if line == "":
                continue
            matches = re.match(r"__start (?P<event>.+) \([^)]+\)", line)
            if matches:
                try:
                    events[self.event_name] = self._save()
                except RuntimeError:
                    pass
                self.event_name = matches.group("event")
                self._reset()
                continue

            matches = re.search(
                r"(?P<url>https://broadcast.amazon.com/live/[a-zA-Z0-9_.-]+)", line
            )
            if matches:
                self.broadcast_url = matches.group("url")
                continue

            if not any([self.meeting_id, self.meeting_pin]):
                matches = re.search(
                    r"(chime.aws/(?P<pin>[a-zA-Z0-9._-]{12,35}|[0-9]{10})|(?P<pin2>[0-9]{10})#|(?P<pin3>[0-9]{4} [0-9]{2} [0-9]{4}))",
                    line,
                )
                if matches:
                    if self.event_name is not None:
                        pin = self._first_valid_item(
                            matches.group("pin"),
                            matches.group("pin2"),
                            matches.group("pin3"),
                        )
                        pin = pin.replace(" ", "")
                        if pin not in ["dialinnumbers"]:
                            if pin.isnumeric():
                                self.meeting_pin = pin
                            else:
                                self.meeting_id = pin
                    continue

            matches = re.match(
                r" {4}(?P<start>\d{1,2}:\d\d(?P<ampm> am| pm)?) - (?P<end>\d{1,2}:\d\d(?P<ampmend> am| pm)?)",
                line,
            )
            if matches:
                self.start_time = matches.group("start")
                self.end_time = matches.group("end")
                if matches.group("ampm"):
                    self.sort_time = time.strftime(
                        "%H:%M", time.strptime(self.start_time, "%I:%M %p")
                    )
                else:
                    self.sort_time = self.start_time
                continue

            matches = re.search(
                r"Join Microsoft Teams Meeting<(?P<url>https://teams.microsoft.com/l/meetup-join/[^>]+)>",
                line,
            )
            if matches:
                self.teams_url = matches.group("url")
                continue

            matches = re.search(
                r"(?P<url>https://meet.google.com/[a-z]{3}-[a-z]{4}-[a-z]{3})", line
            )
            if matches:
                self.meet_url = matches.group("url")
                continue
        try:
            events[self.event_name] = self._save()
        except RuntimeError:
            pass

        if not len(events):
            wf.warn_empty("No more meetings with Chime/Broadcast info were found")
        else:
            sorted_events = OrderedDict(
                sorted(events.items(), key=lambda t: t[1].sort_time)
            )
            for key in sorted_events.keys():
                event = events[key]
                wf.add_item(
                    "{}".format(event.event_name),
                    event.description(),
                    arg=event.url(),
                    valid=True,
                    icon=event.icon(),
                )
        self.events = events
        wf.send_feedback()


if __name__ == "__main__":
    wf = Workflow3()
    cs = CalendarScanner()
    sys.exit(wf.run(cs.get_events))
