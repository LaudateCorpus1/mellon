import mellon
from sparc.testing.testlayer import SparcZCMLFileLayer

import os
import shutil
import tempfile
from zope import component

DEFAULT_snippet_lines_increment = 2
DEFAULT_snippet_lines_coverage = 5
DEFAULT_read_size = 512000
DEFAULT_snippet_bytes_increment = 7
DEFAULT_snippet_bytes_coverage = 8

class MellonFactoriesFilesystemLayer(SparcZCMLFileLayer):
    
    def create_file(self, rel_path_list, type_, length):
        if type_ == 'binary':
            with open(os.path.join(self.working_dir, *rel_path_list), 'w+b') as file:
                file.write(os.urandom(length))
        else:
            with open(os.path.join(self.working_dir, *rel_path_list), 'w+t') as file:
                file.writelines(['{}{}'.format(i+1,os.linesep) for i in range(length)])

    def setUp(self):
        SparcZCMLFileLayer.setUp(self)
        """
        1
         /a
           exact.txt
           exact.bin
         /b
           [empty]
         largest.txt
         largest.bin
        2
         /c
           [empty]
         /d
           larger.txt
           larger.bin
        small.txt
        small.bin
        
        *-small => smaller than coverage
        *-exact => exact size as coverage
        *-larger => a little larger than coverage
        *-largest => much larger than coverage
        """
        self.working_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.working_dir, '1','a'))
        os.makedirs(os.path.join(self.working_dir, '1','b'))
        os.makedirs(os.path.join(self.working_dir, '2','c'))
        os.makedirs(os.path.join(self.working_dir, '2','d'))
        
        
        self.create_file(['small.txt'], 'text', 4)
        self.create_file(['small.bin'], 'binary', 128)
        
        self.create_file(['1','largest.txt'], 'text', 1024)
        self.create_file(['1','largest.bin'], 'binary', 2*DEFAULT_read_size*DEFAULT_snippet_bytes_coverage)
        
        self.create_file(['1','a','exact.txt'], 'text', 5)
        self.create_file(['1','a','exact.bin'], 'binary', DEFAULT_read_size*DEFAULT_snippet_bytes_coverage)
        
        self.create_file(['2','d','larger.txt'], 'text', 8)
        self.create_file(['2','d','larger.bin'], 'binary', DEFAULT_read_size*DEFAULT_snippet_bytes_coverage+DEFAULT_read_size)
        
        config = {'MellonSnippet':
                          {
                           'lines_increment': DEFAULT_snippet_lines_increment,
                           'lines_coverage': DEFAULT_snippet_lines_coverage,
                           'bytes_read_size': DEFAULT_read_size,
                           'bytes_increment': DEFAULT_snippet_bytes_increment,
                           'bytes_coverage': DEFAULT_snippet_bytes_coverage
                           },
                       'FileSystemDir':
                           {
                            'directory': self.working_dir
                           }
                      }
        self.config = component.createObject(u'sparc.configuration.container', config)
    
    def tearDown(self):
        if len(self.working_dir) < 3:
            print('ERROR: working directory less than 3 chars long, unable to clean up: %s' % str(self.working_dir))
            return
        shutil.rmtree(self.working_dir)
        SparcZCMLFileLayer.tearDown(self)

MELLON_FACTORIES_FILESYSTEM_LAYER = MellonFactoriesFilesystemLayer(mellon)