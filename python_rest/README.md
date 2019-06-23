# URL Shortener

Web API que retorna links recortados de urls.

### Pre-requisitos 📋

Python 2.7 y todos los modulos:
* functools
* short_url
* flask
* flask_limiter
* flask_jsonpify
* flask_httpauth
* flask_sqlalchemy
* sqlite3
* logging

### Instalación 🔧

Primero se debe ejecutar python createTables.py

## Ejecutando las pruebas ⚙️

Con [ip] = 127.0.0.1

* Crear Usuario

curl -i -X POST \
   	-H "Content-Type: application/json" \
   	-d '{"username":"alejo","password":"python"}' \
   	http://[ip]:5002/api/v1.0/users

* Login

curl -u alejo:python -i -X GET \
	http://[ip]:5002/api/v1.0/login

* Agregar URL

curl -i -X POST \
  	-H "Content-Type: application/json" \
  	-d '{"url_long_name":"https://www.youtube.com"}' \
  	http://[ip]:5002/api/v1.0/add_url

* Desde el Browser

http://[ip]:5002/api/v1.0/url/clickStats?shortUrl=pbq8b&apiKey=ABCDEF123456789
http://[ip]:5002/api/v1.0/url/shorten?longUrl=https://www.youtube.com&apiKey=ABCDEF123456789
http://[ip]:5002/api/v1.0/url/shorten?longUrl=https://www.google.com&apiKey=ABCDEF123456789
http://[ip]:5002/api/v1.0/url/expand?shortUrl=25t52&apiKey=ABCDEF123456789
http://[ip]:5002/api/v1.0/url?apiKey=ABCDEF123456789
http://[ip]:5002/api/v1.0/?apiKey=ABCDEF123456789
http://[ip]:5002/api/v1.0/

### Y las pruebas de estilo de codificación ⌨️

* Pylint
* Autopep8

## Deployment 📦

Ejecutar python server.py

## Herramientas 🛠️

* Linux Mint
* Python 2.7
* Flask
* GIT
* VIM
* Pylint
* Autopep8
