FROM openknowledge/rt

RUN rm /etc/service/postfix/run

ADD ./svc/postfix/run /etc/service/postfix/run
ADD ./postfix/main.cf /etc/postfix/main.cf
ADD ./postfix/aliases /etc/postfix/aliases 
ADD ./postfix/procmailrc.rt /etc/postfix/procmailrc.rt

RUN newaliases -C /etc/postfix
