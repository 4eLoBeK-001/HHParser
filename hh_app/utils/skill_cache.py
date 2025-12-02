from hh_app.models import Skill

class SkillCache:
    _cache: set[str] | None = None

    @classmethod
    def get(cls) -> set[str]:
        if cls._cache is None:
            cls._cache = set(Skill.objects.values_list('name', flat=True))
        return cls._cache
    
    @classmethod
    def add(cls, skills: set[str]):
        cls.get()
        cls._cache.update(skills)