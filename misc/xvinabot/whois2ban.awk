#!/usr/bin/awk -f

function dq2dec(dq) {
	parts = split(dq, b, ".");
	dec = b[4] + b[3]*256 + b[2]*256*256 + b[1]*256*256*256;
	return dec;
}

BEGIN {
	netnum=host;
	netmask=32;
	netname="Unknown";
	country="??";
}
/^inetnum:[ \t]+[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ - [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/ {
	size=dq2dec($4) - dq2dec($2) + 1;
	netnum=$2;
	netmask=sprintf("%.0f", 32 - log(size) * 1.4426950408889634);
}
/^netname:/ { netname=$2; }
/^country:/ { country=$2; }
END {
	if (country == "vn" || country == "VN") {
		printf("route add -net %s/%s reject # %s (%s)\n", netnum, netmask, netname, country);
	} else {
		printf("route add -host %s reject # %s (%s)\n", host, netname, country);
	}
}
