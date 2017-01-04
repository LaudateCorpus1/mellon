from BTrees.OOBTree import OOBTree
from zope import component
from zope import interface
from zope.annotation.interfaces import IAnnotations
from zope.component.factory import Factory
from .interfaces import IApplyAuthorizationContext, IAuthorizationContext, IMellonFile, ISnippet


@interface.provider(IAuthorizationContext)
class AuthorizationContext(object):
    
    def __init__(self, identity, description):
        self.identity = identity
        self.description = description
    
    def __str__(self):
        return "context identity: {} with description: {}".format(self.identity, self.description)
authorizationContextFactory = Factory(AuthorizationContext)

@interface.provider(IAuthorizationContext)
@component.adapter(IMellonFile)
class AuthorizationContextForMellonFile(object):
    
    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(context).\
                                setdefault('IAuthorizationContext', OOBTree())
        if 'identity' not in self.annotations:
            self.annotations['identity'] = u''
        if 'description' not in self.annotations:
            self.annotations['description'] = u''
    
    @property
    def identity(self):
        return self.annotations['identity']
    @identity.setter
    def identity(self, value):
        self.annotations['identity'] = value
    
    @property
    def description(self):
        return self.annotations['description']
    @description.setter
    def description(self, value):
        self.annotations['description'] = value
    
    def __str__(self):
        return "context identity: {} with description: {}".format(self.identity, self.description)

@interface.provider(IAuthorizationContext)
@component.adapter(ISnippet)
class AuthorizationContextForSnippet():
    def __new__(cls, context):
        return AuthorizationContextForMellonFile(context.__parent__)

@interface.provider(IApplyAuthorizationContext)
class ApplyAuthorizationContext(object):
    def __call__(self, context, item):
        item_sec_context = IAuthorizationContext(item)
        item_sec_context.identity = context.identity
        item_sec_context.description = context.description
        return item_sec_context