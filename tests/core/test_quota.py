import pytest

from meridian_core.quota import QuotaTracker, TokenBucket
from meridian_core.errors import RateLimitError
from tests.helpers import state_dir


def test_quota_records_real_calls() -> None:
    quota = QuotaTracker(state_dir("quota-a") / "quota.sqlite3", limit=2, bucket=TokenBucket(capacity=10, tokens=10))
    quota.record_call("search")
    snapshot = quota.snapshot()
    assert snapshot.used_period == 1
    assert snapshot.remaining == 1


def test_token_bucket_blocks_bursts() -> None:
    quota = QuotaTracker(state_dir("quota-b") / "quota.sqlite3", bucket=TokenBucket(capacity=1, tokens=0, refill_per_second=0))
    with pytest.raises(RateLimitError):
        quota.check()
