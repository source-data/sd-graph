

Set up .env from .env.example with appropriate credentials.

Optional: download meca archives from bioRxiv S3:

    aws s3 cp --request-payer requester --recursive --exclude "*" --include "*.meca" s3://biorxiv-src-monthly/Current_Content/March_2020 data/meca

or select meca archives to be processed and place into data/meca

Build the SD graph:

    python -m sdg.sdneo <collection_name>
    cat sdg/SD-processing.cql | cypher-shell -a bolt://localhost:7687 -u <neo4j_username> -p <neo4j_password>

Import JATS XML documents from meca archives:

    python -m neojats.xml2neo path/to/meca

Launch server for REST API:

    export FLASK_APP='neoflask.neoflask'; export FLASK_DEBUG=true; python -m flask run



# With docker-compose

To make sure you start with a clean build you can run. This can solve some issues, for example if you run `build` with a wrong config file.

```
docker-compose -f local.yml build --force-rm --no-cache
```

Normally you just need this:
```bash
docker-compose -f local.yml build
docker-compose -f local.yml up -d
docker-compose -f local.yml run --rm flask python -m sdg.sdneo SARS-CoV-2
# download https://oc.embl.de/index.php/s/sG0cLDYQtIFFejM and unzip in ./data/meca/
cat sdg/SD-processing.cql | docker-compose -f local.yml run --rm neo4j cypher-shell -a bolt://neo4j:7687 -u neo4j -p <NEO4J_PASSWORD>
docker-compose -f local.yml run --rm flask python -m neojats.xml2neo data/meca
```



# Production
add something like this to your local `~/.ssh/config`

```
Host covid19-1 ec2-3-125-193-124.eu-central-1.compute.amazonaws.com
  Hostname ec2-3-125-193-124.eu-central-1.compute.amazonaws.com
  User ec2-user
  IdentityFile ~/.ssh/id_rsa
```

## first setup
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

## Deploying
Something like this will (generally) be enough, but really depends on your changes :)

```bash
git pull
docker-compose -f production.yml build
docker-compose -f production.yml up -d
```