* Run the web server

    export FLASK_APP=neoflask; export FLASK_DEBUG=true; python -m flask run


# Run with Docker

```
docker-compose -f local.yml build
docker-compose -f local.yml up -d
docker-compose -f local.yml down
```

You need to create a folder called `neo4j-data` at the root of your project.
After you run it once, it will be populated. After that you can replace it with your backed up data.


## dump neo4j
_taken from https://serverfault.com/questions/835092/how-do-you-perform-a-dump-of-a-neo4j-database-within-a-docker-container_

With all the docker services stopped (`docker-compose -f local.yml down`)

```
docker run --volume=$PWD/neo4j-data:/data -it neo4j:3.5 neo4j-admin dump --database=graph.db --to=/data/backups/`date +%Y-%m-%d-%T`.dump
```

## load for production
With all the docker services stopped (`docker-compose -f production.yml down`)
```
docker run --volume=neoflask_production_neo4j_data:/data --volume=$PWD/neo4j-data/backups:/backups -it neo4j:3.5 neo4j-admin load --from=/backups/2020-04-10.dump --database=graph.db --force
```