BEGIN { count=0; rss=0; }

/^[a-z][^ \t]+[ \t]+[0-9]/ {
    count = count + 1;
    rss = rss + $6;
}

END { printf("%s:%s:%s\n", host, count, rss); }
