from zope import interface

class IConfiguredAssignablesStatuses(interface.Interface):
    def items():
        """Iterator of (value, token, description) tuples of workflow assignable statuses"""