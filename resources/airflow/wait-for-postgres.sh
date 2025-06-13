#!/bin/bash
# wait-for-postgres.sh

host="$1"
shift
cmd="$@"

echo "Esperando a que Postgres esté listo en $host..."

until pg_isready -h "$host" -p 5432; do
  echo "Postgres no disponible, esperando 2 segundos..."
  sleep 2
done

echo "Postgres está listo, ejecutando el comando."
exec $cmd
