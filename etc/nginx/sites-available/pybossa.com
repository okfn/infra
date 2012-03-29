server {
	server_name  pybossa.com demo.pybossa.com;

	access_log  /var/log/nginx/pybossa.com.access.log;

	server_name_in_redirect  off;

	location / {
		proxy_pass http://localhost:5030;
		proxy_redirect off;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	}

}

