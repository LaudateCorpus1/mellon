import os.path
from zope import component
from zope import interface
from zope.component.factory import Factory
import mellon
from mellon.factories.filesystem.file import MellonByteFileFromFilePathAndConfig
from mellon.factories.filesystem.file import \
                                        MellonUnicodeFileFromFilePathAndConfig

@interface.implementer(mellon.IByteMellonFile)
class MellonByteFileFromGitRepoCommitPathAndConfig(
                                        MellonByteFileFromFilePathAndConfig):
    
    def __init__(self, commit, file_path, config, parent_override=None):
        self.commit = commit
        self._parent_override = parent_override or self
        super(MellonByteFileFromGitRepoCommitPathAndConfig, self).\
                                                    __init__(file_path, config, parent_override=self._parent_override)
        
    def __str__(self):
        return "Git byte file in repo at {} for commit {} at location {}".\
                    format(self.commit.repo.working_dir, 
                           str(self.commit), self.file_path)
mellonByteFileFromGitRepoCommitPathAndConfigFactory = \
                        Factory(MellonByteFileFromGitRepoCommitPathAndConfig)

@interface.implementer(mellon.IUnicodeMellonFile)
class MellonUnicodeFileFromGitRepoCommitPathAndConfig(
                                        MellonUnicodeFileFromFilePathAndConfig):
    
    def __init__(self, commit, file_path, config, parent_override=None):
        self.commit = commit
        self._parent_override = parent_override or self
        super(MellonUnicodeFileFromGitRepoCommitPathAndConfig, \
                                            self).__init__(file_path, config, parent_override=self._parent_override)
        
    def __str__(self):
        return "Git unicode file in repo at {} for commit {} at location {}".\
                    format(self.commit.repo.working_dir, 
                           str(self.commit), self.file_path)
mellonUnicodeFileFromGitRepoCommitPathAndConfigFactory = \
                        Factory(MellonUnicodeFileFromGitRepoCommitPathAndConfig)
        

@interface.implementer(mellon.IMellonFileProvider)
class MellonFileProviderForGitReposBaseDirectory(object):
    
    def __init__(self, config):
        """Init
        
        Args:
            config: sparc.config.IConfigContainer
                    provider with sparc.git[configure.yaml:GitReposBaseDir]
                    and mellon[configure.yaml:MellonSnippet] entries.
        """
        self.config = config
    
    def __iter__(self):
        repos_base_dir = self.config.mapping().get_value('GitReposBaseDir')['directory']
        
        repo_iter = component.createObject(\
                u'sparc.git.repos.repos_from_recursive_dir', repos_base_dir)
        for repo in repo_iter:
            # iterate through the commits
            examined = set()
            for commit in repo.iter_commits('--all'):
                # we need to reset the working tree to gain filesystem access
                # to the blob data.  This will allow us to pass in a path
                # (needed to determine if file is binary or not)
                repo.head.reference = commit
                repo.head.reset(index=True, working_tree=True)
                # iter through commit blobs (e.g. files)
                for blob in commit.tree.traverse():
                    if blob.type != 'blob' or blob.hexsha in examined:
                        continue
                    else:
                        examined.add(blob.hexsha)
                        if not os.path.isfile(blob.abspath):
                            continue
                    path = component.createObject(u"mellon.filesystem_path", blob.abspath)
                    #path = provider(blob.abspath)
                    #interface.alsoProvides(path, mellon.IPath)
                    if mellon.IBinaryChecker(path).check():
                        yield component.createObject(\
                            u'mellon_plugin.factory.git.byte_file_from_commit_path_and_config',
                            commit,
                            path,
                            self.config)
                    else:
                        yield component.createObject(\
                            u'mellon_plugin.factory.git.unicode_file_from_commit_path_and_config',
                            commit,
                            path,
                            self.config)
MellonFileProviderForGitReposBaseDirectoryFactory = Factory(MellonFileProviderForGitReposBaseDirectory)
interface.alsoProvides(MellonFileProviderForGitReposBaseDirectoryFactory, mellon.IMellonFileProviderFactory)