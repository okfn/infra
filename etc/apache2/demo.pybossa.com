<VirtualHost *:80>
    ServerName demo.pybossa.com

    # WSGIScriptAlias / /home/okfn/var/srvc/demo.pybossa.com/bin/demo.pybossa.com.wsgi
    # WSGIDaemonProcess demo.pybossa.com display-name=demo.pybossa.com processes=4 threads=1 maximum-requests=1000

    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/

    ErrorLog /var/log/apache2/demo.pybossa.com.error.log
    CustomLog /var/log/apache2/demo.pybossa.com.custom.log combined
</VirtualHost>

