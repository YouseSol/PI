import enum
import pydantic


class ChatStatus(enum.Enum):
    KEEP_ANSWERING = "KeepAnswering"
    NEED_INTERVENTION = "NeedIntervention"
    WANT_TO_SCHEDULE_MEETING = "ScheduleMeeting"

class ChatAction(pydantic.BaseModel):
    status: ChatStatus = ChatStatus.KEEP_ANSWERING

    should_answer: bool
    message: str | None = None
