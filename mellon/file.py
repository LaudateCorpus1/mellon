import collections
from zope import component
from zope import interface
from zope.component.factory import Factory
from sparc.configuration import container
from .interfaces import IByteMellonFile, IUnicodeMellonFile

DEFAULT_snippet_lines_increment = 1
DEFAULT_snippet_lines_coverage = 5
DEFAULT_read_size = 512000
DEFAULT_snippet_bytes_increment = 7
DEFAULT_snippet_bytes_coverage = 8

@interface.implementer(IByteMellonFile)
class MellonByteFileFromFileStreamAndConfig(object):
    
    def __init__(self, file_stream, config, snippet_interfaces=None):
        self.file_stream = file_stream
        self.config = config
        self.snippet_interfaces = snippet_interfaces
        
        snippet_config = container.\
                            IPyContainerConfigValue(config).get('MellonSnippet')
        
        self.read_size = snippet_config.get(\
                            'bytes_read_size', DEFAULT_read_size)
        self.snippet_bytes_increment = snippet_config.get(\
                            'bytes_increment', DEFAULT_snippet_bytes_increment)
        self.snippet_bytes_coverage = snippet_config.get(\
                            'bytes_coverage', DEFAULT_snippet_bytes_coverage)
        
    def __str__(self):
        return "byte file at location {}".format(self.file_stream)
    
    def _buffer_snippet(self, buffer, end):
        length = sum([len(d) for d in buffer])
        start = end-length
        snippet = component.createObject(u'mellon.bytes_snippet', 
                            snippet=b"".join(buffer),
                            name=u'position {} for {} bytes'.format(start, length),
                            parent=self)
        if self.snippet_interfaces:
            interface.alsoProvides(snippet, *self.snippet_interfaces)
        return snippet

    def __iter__(self):
        _end = 0
        _buffer = collections.deque()
        _eof_buffer = collections.deque()
        
        _end = 0 #pointer location
        data = self.file_stream.read(self.read_size)
        while data != b'':
            # add line to buffer
            _buffer.append(data)
            _end += len(data)
            # empty over full buffer based on snippet increments
            if len(_buffer) > self.snippet_bytes_coverage:
                _eof_buffer = collections.deque()
                for i in range(self.snippet_bytes_increment):
                    _eof_buffer.append(_buffer.popleft())
            # yield full buffer snippet
            if len(_buffer) == self.snippet_bytes_coverage:
                yield self._buffer_snippet(_buffer, _end)
            #advance the pointer
            data = self.file_stream.read(self.read_size)
            
        # yield for files smaller than coverage
        if len(_buffer) and len(_buffer) < self.snippet_bytes_coverage:
            # if we have a _eof_buffer, we need to left-fill _buffer
            # with _eof_buffer lifo fashion.  This helps insure that
            # snippet_bytes_coverage is met
            while _eof_buffer:
                if len(_buffer) >= self.snippet_bytes_coverage:
                    break
                _buffer.appendleft(_eof_buffer.pop())
            yield self._buffer_snippet(_buffer, _end)
mellonByteFileFromFileStreamAndConfigFactory = Factory(MellonByteFileFromFileStreamAndConfig)

@interface.implementer(IUnicodeMellonFile)
class MellonUnicodeFileFromFileStreamAndConfig(object):
    
    def __init__(self, file_stream, config, snippet_interfaces=None):
        self.file_stream = file_stream
        self.config = config
        self.snippet_interfaces = snippet_interfaces
        
        snippet_config = container.\
                            IPyContainerConfigValue(config).get('MellonSnippet')

        self.snippet_lines_increment = snippet_config.get(\
                        'lines_increment', DEFAULT_snippet_lines_increment)
        self.snippet_lines_coverage = snippet_config.get(\
                        'lines_coverage', DEFAULT_snippet_lines_coverage)
        
    def __str__(self):
        return "unicode file at location {}".format(self.file_stream)
    
    def _buffer_snippet(self, buffer, end):
        start = end-len(buffer)+1
        snippet = component.createObject(u'mellon.unicode_snippet', 
                            snippet=u"".join(buffer),
                            name=u'starting at line {} for {} lines'.format(start, len(buffer)),
                            parent=self)
        if self.snippet_interfaces:
            interface.alsoProvides(snippet, *self.snippet_interfaces)
        return snippet
    
    def _process_line(self, line):
        """Class extenders can override this method to manipulate the buffered line"""
        return line

    def __iter__(self):
        _end = 0
        _buffer = collections.deque()
        _eof_buffer = collections.deque()
        for line in self.file_stream:
            # add line to buffer
            _buffer.append(self._process_line(line))
            _end += 1
            # empty over full buffer based on snippet increments
            if len(_buffer) > self.snippet_lines_coverage:
                _eof_buffer = collections.deque()
                for i in range(self.snippet_lines_increment):
                    _eof_buffer.append(_buffer.popleft())
            # yield full buffer snippet
            if len(_buffer) == self.snippet_lines_coverage:
                yield self._buffer_snippet(_buffer, _end)
            
        # yield for files smaller than coverage
        if len(_buffer) and len(_buffer) < self.snippet_lines_coverage:
            # if we have a _eof_buffer, we need to left-fill _buffer
            # with _eof_buffer lifo fashion.  This helps insure that
            # snippet_lines_coverage is met
            while _eof_buffer:
                if len(_buffer) >= self.snippet_lines_coverage:
                    break
                _buffer.appendleft(_eof_buffer.pop())
            yield self._buffer_snippet(_buffer, _end)
mellonUnicodeFileFromFileStreamAndConfigFactory = Factory(MellonUnicodeFileFromFileStreamAndConfig)

"""
These components are abit of a hack in order to be able to manipulate 
Unicode data that is parsed.  An example of when 
"""