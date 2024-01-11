import uuid


def id_factory() -> str:
    return str(uuid.uuid4())
