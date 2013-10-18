## parse ansible's inventory and extract hostnames
BEGIN { state = "none"; }
/^$/ { state = "none"; }
{ if (state == "group") print $1; }
/^\[[^:\]]*\]/ { state = "group"; }
/^\[[^:\]]:[^\]]*\]/ { state = "child"; }
