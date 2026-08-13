"""Typed records flowing through the pipeline.

These are the contract between graph nodes: Ingest produces Meeting/AgendaItem,
Extract enriches AgendaItem, Impact produces ImpactAssessment.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class Stage(str, Enum):
    """Where an item sits in the meeting. `CONSENT` is the highest-value signal:
    consent items pass in a single block with no discussion unless pulled."""

    CONSENT = "consent"
    ACTION = "action"
    PUBLIC_HEARING = "public_hearing"
    INFORMATIONAL = "informational"
    UNKNOWN = "unknown"


class Attachment(BaseModel):
    name: str
    url: str


class AgendaItem(BaseModel):
    """One line on a meeting agenda."""

    id: str
    city: str
    event_id: int
    meeting_date: date | None = None
    body_name: str | None = None

    agenda_number: str | None = None
    matter_file: str | None = None
    title: str
    action_name: str | None = None

    stage: Stage = Stage.UNKNOWN
    attachments: list[Attachment] = Field(default_factory=list)

    # Filled in by later nodes
    addresses: list[str] = Field(default_factory=list)
    amounts: list[float] = Field(default_factory=list)

    @property
    def is_substantive(self) -> bool:
        """Legistar assigns a matter file only to actual legislative matters.

        Verified against Oakland event 9560: 61/61 items with a matter file are
        real business; 17/17 without one are procedural (headers, roll call,
        ADA notices, adjournment). Note that procedural items *do* get agenda
        numbers — "Call To Order" is item 1 — so the agenda number is not a
        usable signal here.
        """
        return self.matter_file is not None


class Meeting(BaseModel):
    """A single meeting of a legislative body."""

    event_id: int
    city: str
    date: datetime | None = None
    body_name: str | None = None
    agenda_url: str | None = None
    minutes_url: str | None = None
    items: list[AgendaItem] = Field(default_factory=list)

    @property
    def substantive_items(self) -> list[AgendaItem]:
        return [i for i in self.items if i.is_substantive]
