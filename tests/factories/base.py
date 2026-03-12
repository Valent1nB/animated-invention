from factory.alchemy import SQLAlchemyModelFactory


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = None

    @classmethod
    def set_session(cls, session):
        cls._meta.sqlalchemy_session = session  # type: ignore[attr-defined]
