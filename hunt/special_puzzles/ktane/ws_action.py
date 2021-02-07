from enum import Enum

class KtaneActionType(Enum):
    send = 0

class KtaneAction():
    def __init__(self, action_type, msg, targets=None):
        self.action_type = action_type
        self.msg = msg
        self.targets = targets

    def is_send(self):
        return self.action_type == KtaneActionType.send

    @staticmethod
    def make_send(msg, target=None):
        if target is None:
            return KtaneAction(KtaneActionType.send, msg)
        else:
            return KtaneAction(KtaneActionType.send, msg, [target])

    @staticmethod
    def make_send_many(msg, targets):
        return KtaneAction(KtaneActionType.send, msg, targets)
