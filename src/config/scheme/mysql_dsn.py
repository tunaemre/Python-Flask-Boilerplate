from pydantic.networks import MultiHostDsn


class MysqlDsn(MultiHostDsn):
    allowed_schemes = {
        'mysql',
        'mysql+mysqldb',
    }
    user_required = True

    __slots__ = ()
