# boxyellow moinmoin theme #

theme.py  # the moinmoin python theme file
css/     # altered css
  screen.css: new screen.css 
images/  # images for theme

## Installation ##

These are instructions for installation site wide (for use by multiple wikis)

1. python theme: this is in theme.py. You need to install this in the normal
fashion for moinmoin themes:

   [site-wide-moinmoin-python-directory]/boxyellow.py

2. htdocs

  1. In the site-wide htdocs directory copy the modern theme and rename it as
     boxyellow 

  2. Delete (site-wide)/htdocs/boxyellow/css/screen.cs and replace by
     ./css/screen.css

  3. symlink ./images to (site-wide)/htdocs/boxyellow/images

There is a demo wikiconfig.py file in this directory showing some of the
configuration options you can use.

