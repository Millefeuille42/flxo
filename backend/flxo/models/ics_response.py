from fastapi import Response
from ics import Calendar


class ICSResponse(Response):
    media_type = "text/calendar"

    def render(self, content: Calendar | str) -> bytes:
        if isinstance(content, Calendar):
            return content.serialize().encode()
        return content.encode()
