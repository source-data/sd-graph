
# sd-graph
[SourceData](http://sourcedata.embo.org) is a platform built by [EMBO](http://embo.org) in collaboration with [Vital-IT](https://www.vital-it.ch/) to make papers and datasets discoverable based on the experiments shown in figures.

When refering to SourceData, please cite the following paper:

> __SourceData - a semantic platform for curating and searching figures.__
> Liechti R, George N, Götz L, El-Gebali S, Chasapi A, Crespo I, Xenarios I, Lemberger T.
> _Nature Methods_ (2017) __14__:1021 [doi:10.1038/nmeth.4471](http://doi.org/10.1038/nmeth.4471)
Set up .env from .env.example with appropriate credentials.

This repository includes several tools currently under development. These tools allow to generate the SourceData knowledge graph (`sdg`), to upload MECA/JATS archives (`neojats`) as graphs compatible with the SourceData graph and run a server (`neoflask`) that implements pre-formed cypher queries and exposes a RESTful interface for  integration in web applications.

## Build the resource with docker-compose

To make sure you start with a clean build you can run:

```
docker-compose -f local.yml build --force-rm --no-cache
docker-compose -f local.yml down --volumes # to clean the content of the volumes
```

This can solve some issues, for example if you run `build` with a wrong config file.

Normally you just need this:
```bash
docker-compose  build
docker-compose up -d
docker-compose run --rm flask python -m sdg.sdneo SARS-CoV-2 --api sdapi  # import source data public data
docker-compose run --rm flask python -m neotools.rxiv2neo data/meca --type meca # import full text biorxiv preprints
docker-compose run --rm flask python -m neotools.rxiv2neo data/cord19 --type cord19 # import full text MedRxiv preprints (experimental)
docker-compose run --rm flask python -m peerreview.neohypo # import peer reviews from hypothesis
docker-compose run --rm flask python -m sdg.sdneo --api eebapi # smarttag covid-19 preprints
cat sdg/SD-processing.cql | docker-compose run --rm neo4j cypher-shell -a bolt://neo4j:7687 -u neo4j -p <NEO4J_PASSWORD>  # generate merged graph
# visit http:/localhost:8080
```

## How to dump the contents of your neo4j database
Inspired by https://serverfault.com/questions/835092/how-do-you-perform-a-dump-of-a-neo4j-database-within-a-docker-container

```bash
# Make sure you dont have your neo4j running:
docker-compose down

docker rm --force neo4j-dump # just in case

# dump the contents of your database using a temporary container
docker run --name neo4j-dump --env-file .env --mount type=bind,source=$PWD/data/neo4j-data,target=/data -it neo4j:3.5 bin/neo4j-admin dump --database=graph.db --to=data/graph.db.dump.`date +%Y-%m-%d-%H.%M.%S`

# remove the container
docker rm --force neo4j-dump
```

## How to load  contents into your neo4j database

```bash
# Make sure you dont have your neo4j running:
docker-compose down

docker rm --force neo4j-load # just in case

# maker sure there is no database named graph.db
# IRREVERSIBLE. ARE YOU SURE?
rm -fr data/neo4j-data/database/graph.db

# load the contents of your database using a temporary container
docker run --name neo4j-load --env-file .env --mount type=bind,source=$PWD/data/neo4j-data,target=/data -it neo4j:3.5 bin/neo4j-admin load --database=graph.db --from=data/<dump_filename>

# remove the container
docker rm --force neo4j-load
```


## Production

add something like this to your local `~/.ssh/config`

```
Host covid19-1 ec2-3-125-193-124.eu-central-1.compute.amazonaws.com
  Hostname ec2-3-125-193-124.eu-central-1.compute.amazonaws.com
  User ec2-user
  IdentityFile ~/.ssh/id_rsa
```

### First setup

```bash
# ssh into prod
ssh covid19-1

# clone the project
git clone git@github.com:source-data/sd-graph.git
cd sd-graph
git checkout -b jats origin/jats

# initial config
cp .env.example .env # and edit with your desired config
mkdir -p data
cd data
wget https://oc.embl.de/index.php/s/sG0cLDYQtIFFejM/download
unzip download
rm download
cd ..

# build docker
docker-compose -f production.yml build
docker-compose -f production.yml up -d

# and populate the database
docker-compose -f production.yml run --rm flask python -m sdg.sdneo SARS-CoV-2
cat sdg/SD-processing.cql | docker-compose -f production.yml run --rm neo4j cypher-shell -a bolt://neo4j:7687 -u neo4j -p <NEO4J_PASSWORD>
docker-compose -f production.yml run --rm flask python -m neojats.xml2neo data/meca
```

### Deploying
Something like this will (generally) be enough, but really depends on your changes :)

```bash
git pull
docker-compose -f production.yml build
docker-compose -f production.yml up -d
```


# Local non-docker

For local command line usage for debugging, make fist sure `.env` has `NEO_URI=bolt://localhost:7687` and `EEB_PUBLIC_API=http://localhost:5000/api/v1/`

Activate environment

    source .venv/bin/activate

Start local neo4j

    neo4j start

Launch neoflask interface:

    export FLASK_APP=neoflask; export FLASK_ENV=development; export FLASK_DEBUG=true; python -m flask run

Upload meca archives to neo:

    python -m neotools.rxiv2neo data/meca --type meca

Upload sd collection:

    python -m sdg.sdneo <collection name> --api sdapi

Check RESTful interface is active and neo loaded:

    python -m sdg.eebapi -L

Upload and SmartTag COVID19 preprints:

    python -m sdg.sdneo --api eebapi

Process the merged graph:

    cat sdg/SD-processing.cql | cypher-shell -a bolt://localhost:7687 -u neo4j -p <NEO4J_PASSWORD>

Run the app

    cd frontend; npm run serve
