from zope import interface

class IConfiguredAssignablesSeverities(interface.Interface):
    def items():
        """Iterator of (value, token, description) tuples of workflow assignable severities"""