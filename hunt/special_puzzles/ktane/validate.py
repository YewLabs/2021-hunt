# TODO: make this eventually False
ASSERT_VALID = False

class Validator:
    @staticmethod
    def is_nat_str(x):
        if not Validator.is_str(x):
            if ASSERT_VALID:
                raise Exception('validation error')
            return False
        if not x.isdigit():
            if ASSERT_VALID:
                raise Exception('validation error')
            return False
        return True

    @staticmethod
    def is_nat(x, ub=None):
        if type(x) != int or x < 0:
            if ASSERT_VALID:
                raise Exception('validation error')
            return False
        if ub is not None and x >= ub:
            if ASSERT_VALID:
                raise Exception('validation error')
            return False
        return True

    def is_dict(x):
        if type(x) != dict:
            if ASSERT_VALID:
                raise Exception('validation error')
            return False
        return True

    def has_key(x, k):
        if k not in x:
            if ASSERT_VALID:
                raise Exception('validation error')
            return False
        return True

    def is_str(x):
        if type(x) != str:
            if ASSERT_VALID:
                raise Exception('validation error')
            return False
        return True

    def is_bool(x):
        if type(x) != bool:
            if ASSERT_VALID:
                raise Exception('validation error')
            return False
        return True
