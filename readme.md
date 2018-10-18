### Multi-layered proxy router

#### Настройка
* 8080 - стандартный порт прокси-сервера, меняется в traefik.toml
* 8081 - стандартный порт приватного прокси-сервеа, меняется в traefik.toml, **должен быть закрыт снаружи**
* 8082 - стандартный порт панели администратора, меняется в uwsgi.ini

#### Запуск
`# conda env create -f env.yml -n router`  
`# activate router`  

`# python init_db.py 8080 8081 // порт публичного и приватного прокси-сервера`  

`# nohup uwsgi --ini uwsgi.ini & disown`  
`# nohup ./traefik -c traefik.conf`  
