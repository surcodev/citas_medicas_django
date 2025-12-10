mysql -u noroot -h 192.168.100.172 -p --ssl=0

docker-compose down -v
docker-compose up --build -d

docker inspect citas_django | grep -i Restart -A 5
docker inspect mysql_citas | grep -i Restart -A 5

docker exec -it citas_django sh

python manage.py makemigrations partidas_planos 
python manage.py makemigrations clinica 
python manage.py makemigrations productividad 
python manage.py migrate partidas_planos 
python manage.py migrate clinica 
python manage.py migrate productividad 
python manage.py makemigrations 
python manage.py migrate