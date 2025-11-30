from typing import TypedDict, NotRequired

class HHArea(TypedDict):
    id: str
    name: str


class HHEmployer(TypedDict):
    id: str
    name: str
    altermate_url: str


class HHWorkFormatItem(TypedDict):
    id: str
    name: str


class HHExperience(TypedDict):
    id: str
    name: str


class HHSalary(TypedDict):
    from_: NotRequired[int]
    to: NotRequired[int]
    currency: str
    gross: NotRequired[bool]


class HHProfessionalRole(TypedDict):
    id: str
    name: str


class HHVacancy(TypedDict):
    id: str
    name: str
    published_at: str
    alternate_url: str

    employer: HHEmployer
    area: HHArea
    salary: NotRequired[HHSalary]
    work_format: NotRequired[list[HHWorkFormatItem]]
    work_schedule_by_days: NotRequired[list[dict[str, str]]]
    work_hours: NotRequired[list[dict[str, str]]]
    experience: HHExperience
    professional_roles: NotRequired[list[HHProfessionalRole]]

