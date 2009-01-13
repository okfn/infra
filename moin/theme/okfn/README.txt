# OKF moinmoin theme #

okfn.py  # the moinmoin python theme file
css/     # altered css

## Installation ##

These are instructions for installation site wide (for use by multiple wikis)

1. python theme:

Symlink okfn.py into [site-wide-moinmoin-python-directory]/theme

2. htdocs

  1. Copy the modern theme and rename it as okfn
  2. Delete css/commons.css
  3. symlink all files from css/ into site-wide/htdocs/okfn/css (overwriting
     existing files where necessary) 
  4. symlink site/images into site-wide/htdocs/okfn/

