#!/usr/bin/awk -f

## 42.116.222.202 - - [21/Nov/2013:17:39:50 +0000] "GET /mailman/subscribe/lod2?email=D4WGHOSTY@GMAIL.COM&fullname=&pw=123456789&pw-conf=123456789&language=en&digest=0&email-button=Subscribe HTTP/1.1" 499 0 "http://vipserver88.com/member//check/boom/" "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36"

/GET \/mailman\/subscribe\/[^? ]+\?email=[A-Z0-9]+@[A-Z0-9]+\.[A-Z0-9].*pw=123456789/ { print $1; }
