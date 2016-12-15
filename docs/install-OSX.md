# OSX Install Guide
At the end of this guide, you will have the following:
 - lxml, openssl, and some other dev libraries installed to OSX
 - Homebrew OSX package manager installed
 - Homebrew based virtualized Python installation to run Mellon with
 - Python buildout-based runtime installation of Mellon

## Install required system libraries
Mellon and its dependencies require various OS-level libraries to be installed.
 - install Xcode via app store (installs git, and other various tools)
 - install xcode-select (installs lxml)..
   * `xcode-select --install`

## Install Homebrew, wget, Python, and virtualenv
 - install Homebrew
   * `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
 - install wget
   * `brew install wget`
 - install python
   * `brew install python3`
 - install virtualenv
   * `pip3 install virtualenv`

## Create and source a virtual Python environment for Mellon
 - You can create this anywhere
   * `cd ~`
   * `mkdir virtualenv`
   * `cd virtualenv`
   * `virtualenv mellon`
   * `. mellon/bin/activate`

## Clone the Mellon source repo
 - We'll be leveraging Python Buildout to create a runtime environment
   for Mellon.  We'll simply clone the Mellon repo, as it will provide the
   appropriate buildout config and Mellon runtime sample config starters.
   * `cd ~`
   * `git clone https://github.com/CrowdStrike/mellon.git`


## Initialize a buildout folder for the Mellon runtime environment
 - Buildout is a Python tool for creating app runtime environments easily
   * `cd ~/mellon`
   * `pip install zc.buildout`
   * `buildout init`
   * `wget -O bootstrap.py https://bootstrap.pypa.io/bootstrap-buildout.py`

## Run buildout
 - Before running buildout, we need to update some environment variables
   that will enable some Mellon dependencies to compile/install
   * `export CFLAGS=-I/usr/local/opt/openssl/include`
   * `export CXXFLAGS=-I/usr/local/opt/openssl/include`
   * `export LDFLAGS=-L/usr/local/opt/openssl/lib`
 - We can now run the buildout.  This will create a Mellon runtime environment
   within the current working directory.
   * `bin/buildout -c buildout-mellon.cfg`

## Test Mellon execution
 - This will simply display the Mellon help page.  At this point, you have a
   functioning Mellon environment
   * `bin/mellon -h`
