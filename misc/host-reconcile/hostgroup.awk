## parse ansible's inventory and extract hostnames
BEGIN {
    state = "none"; 
}
/^$/ { state = "none"; }
{ 
    if (state == "group")
	if(hosts[$1]) {
	    hosts[$1] = hosts[$1] "," group;
	} else {
	    hosts[$1] = group;
	}
}
/^\[[^:\]]*\]/ {
    state = "group";
    gsub(/[\[\]]/, "");
    group = $1;
}
/^\[[^:\]]:[^\]]*\]/ { state = "child"; }

END {
    for (host in hosts) {
	printf("%s:%s\n", host, hosts[host]);
    }
}
