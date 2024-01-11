import pytest
from celery import Celery
from celery.local import PromiseProxy
from pydantic.utils import import_string


@pytest.mark.usefixtures('celery')
class TestBeatSchedules:

    def test_beat_schedule(self, celery: Celery):
        beat_schedule = celery.conf.beat_schedule
        assert len(beat_schedule) > 0

        for key in beat_schedule:
            beat = beat_schedule[key]
            # try to load task
            task = import_string(beat['task'])
            # assert task is a celery task
            assert isinstance(task, PromiseProxy)
