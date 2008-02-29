Provide feed aggregation for OKFN.

  1. activity.okfn.org: aggregate activity information regarding OKFN projects.
  2. planet.okfn.org: aggregate open knowledge related blog feeds. (not yet operational)

Currently we use planetplanet [1][] to provide this facility.

[1]:http://www.planetplanet.org/

## INSTALL

1. Install planetplanet. (apt-get install planet or grab the source form [1]).

2. Run the planet script on the relevant config file e.g.

       $ planet.py pathto/config.ini

   or
       
       $ planetplanet pathto/config.ini

   Note that the configuration files can be found in subdirectories
   named after the particular aggregation project.

3. symlink the output directory (usually in same directory as config.ini) to
   wherever the webserver is expecting the directory to be (or alternatively
   point the webserver at this output directory).
