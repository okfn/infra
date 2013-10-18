BEGIN {
    printf("HOST\t\t\tRSS%\tBUF%\tCACHE%\tSWAP%\tTotal(kB)\n");
}
{
    if($4 == 0) {
	memusage = "NaN";
    } else {
	memusage=$3/$4;
    }
    if($4 == 0) {
	bufusage = "NaN";
    } else {
	bufusage = $5/$4;
    }
    if($4 == 0) {
	cacheusage = "NaN";
    } else {
	cacheusage = $6/$4;
    }
    if($7 == 0) {
	swapusage = "NaN";
    } else {
	swapusage = ($7-$8)/$7;
    }
    printf("%s\t%.02f\t%.02f\t%.02f\t%.02f\t%d", 
	   $1, memusage, bufusage, cacheusage, swapusage, $4);
    printf("\n");
}
