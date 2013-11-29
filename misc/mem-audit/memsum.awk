BEGIN { mem=0; cached=0; buffers=0; swapt=0; swapf=0; }

/^MemTotal:/ {
    mem=$2;
}
/^Cached:/ {
    cached=$2;
}
/^Buffers:/ {
    buffers=$2;
}
/^SwapTotal:/ {
    swapt=$2;
}
/^SwapFree:/ {
    swapf=$2;
}

END { printf("%s:%s:%s:%s:%s:%s\n", host, mem, buffers, cached, swapt, swapf); }
