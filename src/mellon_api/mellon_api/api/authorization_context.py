from zope import interface
from mellon_plugin.reporter.sqlalchemy.orm import IORMAuthorizationContext
from marshmallow_jsonapi import Schema, fields

@interface.implementer(IORMAuthorizationContext)
class MMJsonAuthorizationContext(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True)

    class Meta:
        type_ = 'authorization_contexts'
        self_url = '/authorization_contexts/{id}'
        self_url_kwargs = {'id': '<id>'}
        self_url_many = '/authorization_contexts/'
        strict = True

#@app.route('/authorization_contexts/', methods=['GET'])
def APIAuthorizationContext():
    pass