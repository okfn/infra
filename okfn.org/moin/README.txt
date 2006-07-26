# OKF moinmoin theme #

okfn.py  # the moinmoin python theme file
css/     # altered css
  master.css: symlink to ../site/styles/master.css
  css/screen.css: new screen.css which just adds a few extra items to master.css

## Installation ##

These are instructions for installation site wide (for use by multiple wikis)

1. python theme:

Symlink okfn.py into [site-wide-moinmoin-python-directory]/theme

2. htdocs

  1. Create okfn directory in site-wide moinmoin htdocs directory.
  2. Copy the modern theme and rename it as okfn
  3. symlink all files from css/ into htdocs/okfn/css (overwriting existing
     files where necessary) 
  4. symlink site/images into htdocs/

