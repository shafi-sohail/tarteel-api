from pinax.badges.base import Badge, BadgeAwarded, BadgeDetail
from pinax.badges.registry import badges


class DaysBadge(Badge):
    """Number of consecutive days a user has logged in."""
    slug = "days"
    levels = [
        BadgeDetail(name='3 Days', description="Active for 3 days in a row."),
        BadgeDetail(name='1 Week', description="Active for 7 days in a row."),
        BadgeDetail(name='1 Month', description="Active for 30 days in a row."),
        BadgeDetail(name='6 Month', description="Active for 6 months in a row."),
        BadgeDetail(name='1 Year', description="Active for 365 days in a row."),
    ]
    events = [
        "login",
    ]
    multiple = False

    def award(self, **state):
        user = state["user"]
        points = user.get_profile().login_points
        if points > 3:
            return BadgeAwarded(level=1)
        elif points > 7:
            return BadgeAwarded(level=2)
        elif points > 30:
            return BadgeAwarded(level=3)
        elif points > 180:
            return BadgeAwarded(level=4)
        elif points > 365:
            return BadgeAwarded(level=5)


class AyahsContributedBadge(Badge):
    """Number of Ayahs a user has contributed."""
    slug = "ayahs_contributed"
    levels = [
        BadgeDetail(name='10 Ayahs', description="Contributed 10 Ayahs."),
        BadgeDetail(name='50 Ayahs', description="Contributed 50 Ayahs."),
        BadgeDetail(name='100 Ayahs', description="Contributed 100 Ayahs."),
        BadgeDetail(name='500+ Ayahs', description="Contributed 500 Ayahs."),
    ]
    events = [
        "points_awarded",
    ]
    multiple = False

    def award(self, **state):
        user = state["user"]
        points = user.get_profile().ayah_points
        if points > 10:
            return BadgeAwarded(level=1)
        elif points > 50:
            return BadgeAwarded(level=2)
        elif points > 100:
            return BadgeAwarded(level=3)
        elif points > 500:
            return BadgeAwarded(level=4)


badges.register(DaysBadge)
badges.register(AyahsContributedBadge)

