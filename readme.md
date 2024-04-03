# Real-time chat
Как развернуть 


# Как запустить
### С Docker-compose
1. Перейти в директорию с файлом
```commandline
cd wb_chat
``` 
2. Собрать Docker-compose образ
```commandline
docker-compose build
```
3. Запустить Docker-compose образ
```commandline
docker-compose up
```

Чтобы подключиться к вебсокету ws://localhost:8000/ws
Он ВСЕ отдает в виде json и принимает только json
Так что не забывай сериализовывать данные в json