server {
    server_name  www.product-open-data.com product-open-data.com pod.okserver.org browser.product.okfn.org;
    index /index.php;
    autoindex off;
	rewrite_log  on;
    root /var/www/product_open_data/www/;

    access_log /var/log/nginx/productopendata.org-access.log;
    error_log /var/log/nginx/productopendata.org-error.log;
	

     location ^~ /phpmyadmin/ {

           auth_basic            "key?";
           auth_basic_user_file  /etc/nginx/.htpasswd;
	location ~ \.php$ {	    
           try_files $uri /index.php;
           include fastcgi_params;
           fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
           fastcgi_pass 127.0.0.1:9001;
	}

     }

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_pass 127.0.0.1:9001;
    } 

    location ~* \.(js|css|png|jpg|jpeg|gif)$ {
             try_files $uri /index.php;
             expires max;
             log_not_found off;
     }

     location = /_.gif {
             expires max;
             empty_gif;
     }

     location ^~ /cache/ {
             deny all;
     }


###Rewrite Rules####

  rewrite ^/$ /index.php?l=en&p=1;
  rewrite ^/search(.*)$ /index.php?l=en&p=100;
  rewrite ^/pss-specification(.*)$ /index.php?l=en&p=101;
  rewrite ^/pss-change-notes(.*)$ /index.php?l=en&p=105;
  rewrite ^/pss-history(.*)$ /index.php?l=en&p=106;
  rewrite ^/pss-profile(.*)$ /index.php?l=en&p=107;
  rewrite ^/data-quality-([0-9]+)(.*)$ /index.php?l=en&p=102&m=$1;
  rewrite ^/data-quality(.*) /index.php?l=en&p=102;
  rewrite ^/terms-of-use(.*)$ /index.php?l=en&p=103;
  rewrite ^/download(.*)$ /index.php?l=en&p=104;
  rewrite ^/pss-change-notes(.*)$ /index.php?l=en&p=105;
  rewrite ^/pss-history(.*)$ /index.php?l=en&p=106;
  rewrite ^/pss-profile(.*)$ /index.php?l=en&p=107;
  rewrite ^/tweets(.*)$ /index.php?l=en&p=109;
  rewrite ^/open-gepir(.*)$ /index.php?l=en&p=110;
  rewrite ^/navigate(.*)$ /index.php?l=en&p=111;
  rewrite ^/brand-list-([0-9]+)(\/)$ /index.php?l=en&p=112&n=$1;
  rewrite ^/product-brand-list-([0-9]+)(.*)$ /index.php?l=en&p=112&m=$1;
  rewrite ^/supporters(.*)$ /index.php?l=en&p=113;
  rewrite ^/owner-list(\/)$ /index.php?l=en&p=114;
  rewrite ^/product-owner-list-([0-9]+)(.*)$ /index.php?l=en&p=114&n=$1;
  rewrite ^/group-list(\/)$ /index.php?l=en&p=114;
  rewrite ^/product-group-list-([0-9]+)(.*)$ /index.php?l=en&p=114&n=$1;
  rewrite ^/smartphone(.*)$ /index.php?l=en&p=115;
  rewrite ^/nutrition_us(.*)$ /index.php?l=en&p=116;
  rewrite ^/(ar|zh|zt|en|fr|ja|es|ru)+(\/)?$ /index.php?l=$1&p=1;
  rewrite ^/(ar|zh|zt|en|fr|ja|es|ru)+\/?([0-9]+)?([a-z0-9A-Z,_-]+)?(.*)$ /index.php?l=$1&p=$2;
  rewrite ^/product/([0-9]+)$ /rest.php?p=$1 last;
 
}
