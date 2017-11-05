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
    CREATE ROLE nobel WITH LOGIN CREATEDB SUPERUSER PASSWORD'v@R@ns1';
    ```
    - Create new database `CREATE DATABASE metsys OWNER nobel ENCODING 'UTF8';`
    - Quit from postgresql-cli `\q`
    - Restore database `psql -U nobel -d metsys -f metsysLatest.dump`
        * If peer authentication failure, then add '-h localhost'
+ Install redis `sudo apt-get install redis-server`
+ Install pip packages from requirements.txt
+ Run a python shell and download nltk package
    - `import nltk`
    - `nltk.download('punkt')`
+ Run server `python manage.py runserver`

## Production Setup
+ Install gunicorn: `pip install gunicorn`
+ Make a gunicorn.service file in /etc/systemd/system:
    - Write this in the file:
    ```
    [Unit]
    Description=gunicorn daemon
    After=network.target

    [Service]
    User=nobel
    Group=www-data
    WorkingDirectory=absolute_path_to_web_app_directory
    ExecStart=/home/user_name/.pyenv/versions/Metsys/bin/gunicorn --access-logfile - --workers 4 --timeout 600 --bind unix:/absolute_path_to_web_app_directory/bazar.sock bazar.wsgi:application

    [Install]
    WantedBy=multi-user.target
    ```
    - change directory names, where necessary
    - Run gunicorn script: `sudo systemctl start gunicorn.service`
+ Install nginx: `sudo apt install nginx`
    - Configure nginx
        * Make a file named `metsys` in /etc/nginx/sites-available/
        * Put configuration data in the file:
        ```
        server {
            listen 80;
            server_name domain_name_or_ip;

            location = /favicon.ico { access_log off; log_not_found off; }
            location /static/ {
                alias absolute_path_to_app_directory/staticfiles/;
            }

            location / {
                include proxy_params;
                proxy_pass http://unix:/home/nobel/Devel/metsys/bazar.sock;
            }
        }
        ```
        * In the web app directory, run `python manage.py collectstatic`
        * Then run: `sudo ln -s /etc/nginx/sites-available/metsys /etc/nginx/sites-enabled/`
        * check configuration files: `sudo nginx -t`
    - Restart nginx: `sudo systemctl restart nginx`
    - If there is any firewall issue, run: `sudo ufw allow 'Nginx Full'`
+ If everything runs correctly, website homepage should be accessible by now.
But channels app is still unaccessible
