# Golden test -- the fixed contract. The agent NEVER edits this; it only
# changes solution.py until every case here passes.
from solution import is_leap_year

CASES = [
    (2000, True),   # divisible by 400 -> leap
    (1900, False),  # divisible by 100 but not 400 -> NOT leap (the tricky one)
    (2024, True),   # divisible by 4, not by 100 -> leap
    (2023, False),  # not divisible by 4 -> not leap
    (1600, True),   # divisible by 400 -> leap
    (2100, False),  # divisible by 100 not 400 -> not leap
]

errors = 0
for year, expected in CASES:
    got = is_leap_year(year)
    if got != expected:
        print(f"FAIL: is_leap_year({year}) -> {got}, expected {expected}")
        errors += 1

if errors == 0:
    print("ALL_TESTS_PASSED")
else:
    print(f"TESTS_FAILED: {errors}")
