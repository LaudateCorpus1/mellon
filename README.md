# MELLON
...Hours later, they're all still there, bored and anxious, Gandolf muttering
away.  The door hasn't budged.  Gandolf sits down, his back to the door, weary,
defeated.  Frodo the hobbit looks up and reads the inscription once again:
"Speak friend and enter."
    "It's a riddle," he says.  "Gandolf, what is the Elvish word for friend?"
    Gandolf looks at him, puzzled, annoyed.
    "Mellon," he says.
    And with the uttering of that one word, the door swings open...

## Got no time?  Here's the quickstart:
**Installation**
 - [OSX Installation Guide](https://github.com/CrowdStrike/mellon/blob/master/docs/install-OSX.md)

**Simple Configuration Samples**

Mellon requires a runtime YAML configuration file.  You can find all the
configuration definitions 
[here](https://github.com/CrowdStrike/mellon/blob/master/mellon/config_definitions.yaml), 
but to help ease your entry into Mellon usage we've also provided these simple 
starter configs for you.
 - [File system scanning](https://github.com/CrowdStrike/mellon/blob/master/config/filesystem.mcfg). 
   This will scan a directory recursively for secrets.  Make sure to update 
   the config file with the directory path you'd like to scan.
   * launch command: `bin/mellon config/filesystem.mcfg`
 - [GIT repo scanning](https://github.com/CrowdStrike/mellon/blob/master/config/git.mcfg).  
   This will scan a directory that contains one or more GIT repositories for 
   secrets.  This will scan all of the GIT database resources and their 
   complete revision histories.  We recommend to to clone your repos from the 
   origin server to a separate area for this scanning (as the scan will 
   perform git checkouts of the full commit history)
   * launch command: `bin/mellon config/git.mcfg`

All the samples leverage the regex based sniffer component whose patterns are
defined [here](https://github.com/CrowdStrike/mellon/tree/master/config/sniffer).  
Feel free to create your own custom match patterns, but if you use different 
files make sure to update the Mellon YAML config file accordingly (it 
will be the _MellonRegexSniffer_ entry)

## What is Mellon?
Mellon is a Python runtime application that looks for secrets (like
app passwords, AWS keys, really anything you consider sensitive) in publication
sources such as websites, source control systems, file systems, others.

## What do people use Mellon for?
Mellon is typically used by both Blue and Red teams (security industry terms
for teams that protect vs. teams that attack) to find keys, credentials, and
other sensitive/desired information in various publication sources such as
file systems, git repos, web sites, others.

## What can I easily do with Mellon?
Perform scans on various sources to look for credentials/keys/secrets.
 - **Filesystems**: scan text and binary files for passwords
 - **Git Repos**: scan repo, including resource revision history
 - **Websites**: Crawl named websites and look for published secrets

You can whitelist certain items to help reduce noise:
 - **Files**: you can whitelist based on a file's identity string
 - **Secrets**: you can whitelist a particular secret found in a file.

## What can I do with Mellon with some effort?
Mellon leverages [Zope Component Architecture](https://docs.zope.org/zope.component/narr.html)
and its runtime registry to determine:
 - where to look for secrets
 - how to look for secrets
 - what secrets to look for
 - what to whitelist
 - How to report matches

This design enables you to customize each of these items at runtime by:
 1. Creating a implementation that conforms to the required item interface
 2. Creating a ZCML-based component registration configuration
 3. Adding the ZCML component registration to the mellon runtime config file

Future documentation improvements will provide sample implementation
instructions for each of these component interfaces and their associated
registration.
