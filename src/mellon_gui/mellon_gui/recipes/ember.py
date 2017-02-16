import subprocess
import logging, os, zc.buildout
from sparc.utils.cli.command import CommandLaunch
logger = logging.getLogger(__name__)

class Ember:

    def __init__(self, buildout, name, options):
        """
        Recipe Options:
            npm: name and or path to Node npm command.  Defaults to first npm
                 command found in environment PATH.
            npm: name and or path to Node bower command.  Defaults to first bower
                 command found in environment PATH.
        """
        self.buildout, self.name, self.options = buildout, name, options
            
    
    def install(self):
        options = self.options
        try:
            _npm = options.get('npm', default='npm').split(os.sep)
            self.npm = CommandLaunch(_npm.pop(), arguments=['install'], parent=os.sep.join(_npm) if _npm else None)
        except LookupError as e:
            logger.error("You must have a valid Node environment installed " +
                         "with npm and bower globally installed.  Please see " +
                         "https://nodejs.org for information on how to " +
                         "install Node JS.  Once Node JS and npm are " +
                         "installed, bower may me installed globally via " +
                         "'npm install -g bower'.  Perform these actions, " +
                         "then run buildout again.")
            raise e
        try:
            _bower = options.get('bower', default='bower').split(os.sep)
            self.bower = CommandLaunch(_bower.pop(), arguments=['install'], parent=os.sep.join(_bower) if _bower else None)
        except LookupError as e:
            logger.error("You must have Node JS bower installed globally.  " +
                         "Please execute 'npm install -g bower' then run " +
                         "buildout again.")
            raise e
        
        buildout_dir = self.buildout['buildout']['directory']
        ember_dir = os.path.join(buildout_dir,'src','mellon_gui','mellon_gui','ember','mellon')
        os.chdir(ember_dir)
        try:
            logger.info("executing 'npm install' within ember project directory {}".format(ember_dir))
            subprocess.check_call(self.npm)
            logger.info("executing 'bower install' within ember project directory {}".format(ember_dir))
            subprocess.check_call(self.bower)
        finally:
            os.chdir(buildout_dir)
        
        _remove = ()
        # these directories will be removed during uninstall
        # Not seeing a great reason to remove these...just takes more time to run buildout
        #_remove =(
        #    os.path.join(ember_dir,'bower_components'),
        #    os.path.join(ember_dir,'dist'),
        #    os.path.join(ember_dir,'node_modules'),
        #    os.path.join(ember_dir,'tmp')
        #    )
        
        return _remove
    
    def update(self):
        pass

