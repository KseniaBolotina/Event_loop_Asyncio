export POSTGRES_USER=user
psql --host 127.0.0.1 -p 5431 -U user -d postgres -c "drop database asyncio_swapi"
psql --host 127.0.0.1 -p 5431 -U user -d postgres -c "create database asyncio_swapi"