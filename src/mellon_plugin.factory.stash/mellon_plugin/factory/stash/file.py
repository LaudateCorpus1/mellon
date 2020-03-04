from zope import component
from zope import interface
from zope.component.factory import Factory
from sparc.config.container import SparcConfigContainer
from mellon import IApplyAuthorizationContext
from mellon import IMellonFileProvider
from mellon import IMellonFileProviderFactory

from sparc.logging import logging
logger = logging.getLogger(__name__)

@interface.implementer(IMellonFileProvider)
class MellonFileProviderFromStashConfig(object):
    
    def __init__(self, config):
        """Init
        
        Args:
            config: sparc.config.IConfigContainer
                    provider with sparc.git.stash[configure.yaml:StashProjectRepos] entry
        """
        self.sm = component.getSiteManager()
        self.config = config
        self.security_context = self.authorization_context()
    
    def authorization_context(self):
        sec_context = component.createObject(u'mellon.authorization_context', )
        sec_context.identity = self.config.mapping()['StashProjectRepos']['StashConnection'].get(
                        'username', default='')
        sec_context.description = self.config.mapping()['StashProjectRepos']['StashConnection'].get(
                        'context', default='')
        return sec_context
    
    def __iter__(self):
        """
        In here, we'll iterate and clone/update the stash repos into a local
        git base dir.  We're only going to pull from 'origin' and we'll make the
        assumption it exists (if future requirements need to be more customizable
        then well add it in later).  Once complete, we'll call and iter the 
        git-based IMellonFileProvider implementation in mellon.git
        """
        stash_repo_iter = component.createObject(\
                        u'sparc.git.repos.stash.repos_iterator', self.config)
        for r in stash_repo_iter:
            origin = r.remotes['origin']
            assert origin.exists()
            origin.fetch('--prune') # makes sure repo has all branches and tags, cleans out old
            
            try:
                r.head.reference
            except TypeError:
                r.head.reference = r.heads[0] # make sure we're not in a detached head state (otherwise, pull won't work)
                r.head.reset(index=True, working_tree=True)
            
            origin.pull()
        
        #the git file provider factory expects a config with both 'GitReposBaseDir'
        # and MellonSnippet.  We have both of those...but not in the same 
        # namespace.  We'll create a new config that contains our desired 
        # values.
        config = {}
        config['GitReposBaseDir'] = self.config['StashProjectRepos']['GitReposBaseDir']
        config['MellonSnippet'] = self.config['MellonSnippet']
        
        git_file_provider = component.createObject(\
                    u'mellon_plugin.factory.git.file_provider_from_git_repos_base_directory',
                    SparcConfigContainer(config))
        for f in git_file_provider:
            self.sm.getUtility(IApplyAuthorizationContext)(self.security_context, f)
            yield f

MellonFileProviderFromStashConfigFactory = Factory(MellonFileProviderFromStashConfig)
interface.alsoProvides(MellonFileProviderFromStashConfigFactory, IMellonFileProviderFactory)