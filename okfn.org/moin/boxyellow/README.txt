# OKF moinmoin theme #

fcuk.py  # the moinmoin python theme file
css/     # altered css
  screen.css: new screen.css 
images/  # images for theme

## Installation ##

These are instructions for installation site wide (for use by multiple wikis)

1. python theme: Symlink okfn.py into
   [site-wide-moinmoin-python-directory]/theme

2. htdocs
  1. In the site-wide htdocs directory copy the modern theme and rename it as
     fcuk

  2. Delete (site-wide)/htdocs/fcuk/css/screen.cs and replace by
     ./css/screen.css (fcuk css)

  3. symlink ./images to (site-wide)/htdocs/fcuk/images

