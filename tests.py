def for_check(match):
    try:
        if 1 <= int(match) <= 100:
            return True
        else:
            return False
    except ValueError:
        return False
