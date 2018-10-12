### Multi-layered proxy router

#### usage:  
`sudo docker build -t router .`  
`sudo docker network create traefik`

`sudo docker run -d --network traefik -v traefik_root:/etc/traefik --name traefik_router -p 8080:80 router`  
`sudo docker run -d --network traefik -v traefik_root:/etc/traefik --name traefik_root -p 80:8080 traefik`

Make sure that 8080 is not exposed
