echo "drop database roundware;" | mysql -uround -pround  
echo "create database roundware;" | mysql -uround -pround
python manage.py syncdb && python manage.py migrate
