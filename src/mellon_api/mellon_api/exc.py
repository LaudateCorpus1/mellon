from werkzeug.exceptions import HTTPException



class ProcessingException(HTTPException):
    """Raised when a preprocessor or postprocessor encounters a problem.

    This exception should be raised by functions supplied in the
    ``preprocessors`` and ``postprocessors`` keyword arguments to
    :class:`APIManager.create_api`. When this exception is raised, all
    preprocessing or postprocessing halts, so any processors appearing
    later in the list will not be invoked.
    The keyword arguments ``id_``, ``href`` ``status``, ``code``,
    ``title``, ``detail``, ``links``, ``paths`` correspond to the
    elements of the JSON API error object; the values of these keyword
    arguments will appear in the error object returned to the client.
    Any additional positional or keyword arguments are supplied directly
    to the superclass, :exc:`werkzeug.exceptions.HTTPException`.
    """

    def __init__(self, id_=None, links=None, status=400, code=None, title=None,
                 detail=None, source=None, meta=None, *args, **kw):
        super(ProcessingException, self).__init__(*args, **kw)
        self.id_ = id_
        self.links = links
        self.status = status
        # This attribute would otherwise override the class-level
        # attribute `code` in the superclass, HTTPException.
        self.code_ = code
        self.code = status
        self.title = title
        self.detail = detail
        self.source = source
        self.meta = meta