"""The organization Docket is filtering on behalf of.

Everything the impact scorer needs to answer "would this group care?" — where
they are, and what they are about. Kept small and declarative so a group can be
onboarded from a short form rather than a config file.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class OrgProfile(BaseModel):
    """A neighborhood association or small community nonprofit."""

    name: str
    city: str = "oakland"

    # Geography: the streets and landmarks the group considers "here".
    # Anything within `radius_m` of one of these counts as nearby.
    anchors: list[str] = Field(default_factory=list)
    radius_m: float = 1200.0

    # Named neighborhoods the group covers, matched textually. Cheaper and more
    # reliable than geocoding for items that name an area rather than an address.
    neighborhoods: list[str] = Field(default_factory=list)

    # What the group is about, in their own words. Drives mission-match for
    # citywide items that carry no geography at all (66% of the agenda).
    mission: str = ""
    interests: list[str] = Field(default_factory=list)

    def mentions_our_area(self, text: str) -> bool:
        lowered = text.lower()
        return any(n.lower() in lowered for n in self.neighborhoods)


# A realistic stand-in used for development and the demo. Modeled on a West
# Oakland neighborhood association: residential streets near the 7th Street
# corridor, concerned with housing, development and traffic safety.
DEMO_ORG = OrgProfile(
    name="West Oakland Neighbors (demo profile)",
    city="oakland",
    anchors=[
        "319 Chester Street, Oakland, CA",
        "7th Street, Oakland, CA",
        "Wood Street, Oakland, CA",
    ],
    radius_m=1500.0,
    neighborhoods=["West Oakland", "Wood Street", "Jack London"],
    mission=(
        "Protect and improve quality of life for West Oakland residents: "
        "housing affordability, responsible development, street safety, "
        "clean and usable public space."
    ),
    interests=[
        "housing",
        "development",
        "zoning",
        "street safety",
        "parks",
        "encampments",
        "code enforcement",
        "transit",
    ],
)
