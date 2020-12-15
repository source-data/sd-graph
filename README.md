
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
docker-compose build --force-rm --no-cache
docker-compose down --volumes # to clean the content of the volumes
```

This can solve some issues, for example if you run `build` with a wrong config file.
#### First time setup:

```bash
docker-compose build
docker-compose up
```

Before you import any dump you need to make sure that Neo4j creates the layout for the databases. You can do that by running:

```
docker-compose run --rm neo4j cypher-shell -a bolt://neo4j:7687 -u neo4j -p THE_SOURCEDATA_USER_PASSWORD
```


#### Updating the database contents
Normally you need this:
```bash
docker-compose  build
docker-compose up -d
cat sdg/SD-indices.cql | docker-compose run --rm neo4j cypher-shell -a bolt://neo4j:7687 -u neo4j -p <NEO4J_PASSWORD>  # define indices
docker-compose run --rm flask python -m sdg.sdneo PUBLICSEARCH --api sdapi  # import source data public data
docker run --rm -it -v ~/.aws:/root/.aws --mount type=bind,source=<volume>/biorxiv/Current_Content/July_2020,target=/root/Current_Content/July_2020 amazon/aws-cli s3 sync --request-payer requester --exclude "*" --include "*.meca" s3://biorxiv-src-monthly/Current_Content/July_2020 ./Current_Content/July_2020/ --dryrun

aws s3 sync --request-payer requester --exclude "*" --include "*.meca" s3://biorxiv-src-monthly/Current_Content/July_2020 <path-to-biorxiv-archive>/biorxiv/Current_content/July_2020/
 # update meca archives; sync to folder outside of docker build scope
cat neotools/purge_prelim.cql | docker-compose run --rm neo4j cypher-shell -a bolt://neo4j:7687 -u neo4j -p  # remove prelim articles obtained from the CrossRef and bioRxiv APIs
docker-compose run --rm flask python -m neotools.rxiv2neo biorxiv/<path_to_meca_archives> --type meca   # import full text biorxiv preprints
docker-compose run --rm flask python -m peerreview.neohypo hypothesis  # import peer reviews from hypothesis
docker-compose run --rm flask python -m peerreview.neohypo rrc19  # import peer reviews from rapid reviews: covid-19
docker-compose run --rm flask python -m peerreview.neohypo pci  # import peer reviews from peer community in
docker-compose run --rm flask python -m peerreview.published  # updates publication status
docker-compose run --rm flask python -m sdg.sdneo refereed-preprints --api eebapi  # smarttag specified collection of preprints
docker-compose run --rm flask python -m sdg.sdneo subject-collections --api eebapi  # smarttag all bioRxiv subject collections
cat sdg/SD-processing.cql | docker-compose run --rm neo4j cypher-shell -a bolt://neo4j:7687 -u neo4j -p <NEO4J_PASSWORD>  # generate merged graph
cat sdg/SD-gds.cql | docker-compose run --rm neo4j cypher-shell -a bolt://neo4j:7687 -u neo4j -p <NEO4J_PASSWORD>  # graph data science algo
docker-compose run --rm flask python -m sdg.algonet  # finds named topics and entity highlights
cat sdg/SD-precompute.cql | docker-compose run --rm neo4j cypher-shell -a bolt://neo4j:7687 -u neo4j -p <NEO4J_PASSWORD>  # precompute the graph used by front end
docker-compose run --rm flask python -m twitter.update --limit-date 2020-07-01  # --GO_LIVE  to go live with Twitter updates
cat sdg/audit.cql | docker-compose run --rm neo4j cypher-shell -a bolt://neo4j:7687 -u neo4j -p <NEO4J_PASSWORD>
# visit http:/localhost:8080
```

## How to dump the content of the neo4j database
Inspired by https://serverfault.com/questions/835092/how-do-you-perform-a-dump-of-a-neo4j-database-within-a-docker-container

```bash
# Make sure you dont have your neo4j running:
docker-compose down

# dump the contents of your database using a temporary container
docker run --rm --name neo4j-dump --env-file .env --mount type=bind,source=$PWD/data/neo4j-data,target=/data -it neo4j:4.1 bin/neo4j-admin dump --database=neo4j --to=data/neo4j.db.dump.`date +%Y-%m-%d-%H.%M.%S`
```

## How to load content into the neo4j database

And then you can you load the download db dump with:

```bash
# Make sure you dont have your neo4j running:
docker-compose down

# load the contents of your database using a temporary container
$ docker run --rm --name neo4j-load --env-file .env --mount type=bind,source=$PWD/data/neo4j-data,target=/data --mount type=bind,source=$PWD,target=/app -it neo4j:4.1 bin/neo4j-admin load --database=neo4j --from=/app/<dump_filename>
 # --force # ADDING --force WILL OVERWRITE EXISTING DB!
# if there is no pre-existing graph.db, then the option --force needs to me ommitted to avoid "command failed: unable to load database: NoSuchFileException"
```


## How to dump in production

```bash
# Make sure you dont have your neo4j running:
docker-compose down

# dump the contents of your database using a temporary container
docker run --rm \
    --name neo4j-dump \
    --env-file .env \
    --mount type=bind,source=$PWD,target=/app \
    --mount type=volume,source=sd-graph_production_neo4j_data,target=/data \
    -it neo4j:3.5 \
    bin/neo4j-admin dump --to=/app/graph.dump.`date +%Y-%m-%d-%H.%M.%S` --database=graph.db

```


## Production

add something like this to your local `~/.ssh/config`

```
Host eeb-1 ec2-3-125-193-124.eu-central-1.compute.amazonaws.com
  Hostname ec2-3-125-193-124.eu-central-1.compute.amazonaws.com
  User ec2-user
  IdentityFile ~/.ssh/id_rsa
```

### First setup

```bash
# ssh into prod
ssh eeb-1

# clone the project
git clone git@github.com:source-data/sd-graph.git
cd sd-graph

# initial config
cp .env.example .env # and edit with your desired config; note: config for hypothes.is or sourcedata API are not needed for produtino
wget https://oc.embl.de/index.php/s/<token>/download


# build docker
docker-compose -f production.yml build

# force load the database with the dump
# THIS WILL OVERWRITE THE EXISTING DB
docker run --rm \
 --name neo4j-load \
 --env-file .env \
 --mount type=bind,source=$PWD,target=/app \
 --mount type=volume,source=sd-graph_production_neo4j_data,target=/data \
 -it neo4j:4.1 \
 bin/neo4j-admin load --from=/app/download --database=neo4j --force  # WILL OVERWRITE!

# start the services
docker-compose -f production.yml up -d --remove-orphans
```


### Deploying
Something like this will (generally) be enough, but really depends on your changes :)

```bash
git pull
docker-compose -f production.yml build
docker-compose -f production.yml up -d --remove-orphans
```
