# Things to do to setup Metsys development environment

+ Install pyenv
+ Install miniconda3-4.3.11 using pyenv: `pyenv install miniconda3-4.3.11`
+ Create virtualenv with miniconda: `pyenv virtualenv miniconda3-4.3.11 Metsys`
    - If metsysCondaRequirements.txt is available, create virtualenv with that: `conda create --name <env_name> --file <this file>`
+ Install postgresql
    ```
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'\nwget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install postgresql postgresql-contrib
    ```
    - If there is duplicate sources in repo list, then
    ```
    sudo apt install python3-apt\nwget https://raw.githubusercontent.com/davidfoerster/apt-remove-duplicate-source-entries/master/apt-remove-duplicate-source-entries.py\nchmod +x apt-remove-duplicate-source-entries.py
    sudo ./apt-remove-duplicate-source-entries.py
    ```
+ Setup postgresql
    - Log into postgresql server `sudo -u postgres psql`
    - Create role nobel
    ```
    CREATE ROLE nobel WITH LOGIN CREATEDB CREATEUSER SUPERUSER PASSWORD'v@R@ns1';
    ```
    - Quit from postgresql-cli `\q`
    - Restore database `pg_restore -d metsys -1 metsysLatest.dump`
+ Install redis `sudo apt-get install redist-server`
+ Install pip packages from requirements.txt
+ Run a python shell and download nltk package
    - `import nltk`
    - `nltk.download('punkt')`
+ Run server `python manage.py runserver`
