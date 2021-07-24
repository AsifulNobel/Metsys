# Things to do to setup Metsys development environment on a fresh Ubuntu 16.04 image

+ Install git: `sudo apt install git`
+ Install pyenv:
```curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash```
+ Install miniconda3-4.3.11 using pyenv: `pyenv install miniconda3-4.3.11`
    - Add conda-forge: `conda config --add channels conda-forge`
+ Create virtualenv with miniconda: `pyenv virtualenv miniconda3-4.3.11 Metsys`
    - If metsysCondaRequirements.txt is available, install: `conda install --file metsysCondaRequirements.txt`
+ Install postgresql
    ```
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list';wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install postgresql postgresql-contrib
    ```
    - If there is duplicate sources in repo list, then
    ```
    sudo apt install python3-apt;wget https://raw.githubusercontent.com/davidfoerster/apt-remove-duplicate-source-entries/master/apt-remove-duplicate-source-entries.py;chmod +x apt-remove-duplicate-source-entries.py
    sudo ./apt-remove-duplicate-source-entries.py
    ```
+ Setup postgresql
    - Log into postgresql server `sudo -u postgres psql`
    - Create role nobel
    ```
    CREATE ROLE nobel WITH LOGIN CREATEDB SUPERUSER PASSWORD '';
    ```
    - Create new database `CREATE DATABASE metsys OWNER nobel ENCODING 'UTF8';`
    - Quit from postgresql-cli `\q`
    - Restore database `psql -U nobel -d metsys -f metsysLatest.dump`
        * If peer authentication failure, then add '-h localhost'
+ Install redis `sudo apt-get install redis-server`
+ Change to previously created environment
+ Install pip packages from requirements.txt
+ Run a python shell and download nltk package
    - `import nltk`
    - `nltk.download('punkt')`
+ Run server `python manage.py runserver`

## Production Setup
+ Stop dev server
+ Change to parent directory
+ clone Metsys-Core repo into metsys-core directory
+ Install nginx: `sudo apt install nginx`
    - Configure nginx
        * Make a file named `metsys` in /etc/nginx/sites-available/
        * Put configuration data in the file:
        ```
        server {
            listen port_number;
            server_name domain_name_or_ip;

            location = /favicon.ico { access_log off; log_not_found off; }
            location /static/ {
                alias /home/nobel/Devel/499_Test/metsys/bazar/staticfiles/;
            }

            location / {
                include proxy_params;
                proxy_pass http://unix:/path_to_this_directory/metsys.sock;

	            proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";

                proxy_connect_timeout       600;
                proxy_send_timeout          600;
                proxy_read_timeout          600;
                send_timeout                600;
            }
        }
        ```
        * In the web app directory, run `python manage.py collectstatic`
        * Then run: `sudo ln -s /etc/nginx/sites-available/metsys /etc/nginx/sites-enabled/`
        * check configuration files: `sudo nginx -t`
    - Restart nginx: `sudo systemctl restart nginx`
    - If there is any firewall issue, run: `sudo ufw allow 'Nginx Full'`
+ If everything runs correctly, website homepage should be accessible by now.
+ Then run daphne: `nohup daphne -u ../metsys.sock bazar.asgi:channel_layer -t 600 >../logs/daphne.out.log 2>../logs/daphne.err.log &`
    - If nginx show metsys.sock related issue in error log, check permission of the file. Use if necessary:
    ```
    chmod o+r path_to_this_directory/metsys.sock
    chmod o+x path_to_this_directory/metsys.sock
    ```
    - nginx logs can be found in `/var/logs/nginx/` directory
+ Next run multiple worker processes, but not more than the number of cores available:
    - `nohup python manage.py runworker >../logs/worker.$processNumber.out.log 2>../logs/worker.$processNumber.err.log &`
+ After that, go to `metsys_core` directory, then run: `nohup python manage.py runserver 8005 &`