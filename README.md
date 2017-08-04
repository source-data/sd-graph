# sd-graph
[Source Data](http://sourcedata.embo.org) is a platform built by [EMBO](embo.org) in collaboration with [Vital-IT](https://www.vital-it.ch/) to make papers and datasets discoverable based on the experiments show in figures.

When refering to SourceData, please cite the following preprint:

> __SourceData - a semantic platform for curating and searching figures.__  
> Robin Liechti, Nancy George, Sara El-Gebali, Lou Götz, Isaac Crespo, Ioannis Xenarios, Thomas Lemberger.  
> _BioRxiv_  (2016), doi: https://doi.org/10.1101/058529  

We provide here instructions to build the SourceData sd-graph database in [neo4j](http://neo4j.com) and examples of analyses.

## Easy install

Install and start the neo4j database according to the instructions provided at http://neo4j.com. __IMPORTANT: To be able to run the commands below with the neo4j-tool, please download the [TAR/ZIP distributions](https://neo4j.com/download/community-edition/).__ The scripts below were tested under neo4j community edition 2.2 and 3.1.4.

Unzip `graph.db.zip` in the `neo4j/data/databases/` directory.

Start neo4j

    neo4j start

That's it.

## Build the database from the SourceData API

To enable the use of the `neo4j-shell` tool, uncomment this line in `neo4j/conf/neo4j.conf`:

    # Enable a remote shell server which Neo4j Shell clients can log in to.
    dbms.shell.enabled=true
    
If you run into trouble due to insufficient memory for Java, you may have to edit `neo4j/conf/neo4j.conf` and increase the Java heap size:

    # Java Heap Size: by default the Java heap size is dynamically
    # calculated based on available system resources.
    # Uncomment these lines to set specific initial and maximum
    # heap size.
    #dbms.memory.heap.initial_size=512m
    #dbms.memory.heap.max_size=512m

Install the [Neo4j Python REST Client](https://pypi.python.org/pypi/neo4jrestclient/) with

    pip install neo4jrestclient
    
or

	easy_install neo4jrestclient 

Don't forget to launch neo4j

    neo4j start

Before populating the database, set some constraints:

    neo4j-shell -file SD-constraints.cql
    
Download the content of the SourceData database through the SourceData API and populate the neo4j database (Warning: this will take a while, so be patient...):

    python sdneo.py --password <your_password_to_your_neo4j_instance> PUBLICSEARCH
  
Next, build the relationships to create the sd-graph model:

    neo4j-shell -file SD-processing.cql

This will create the following model, linking papers, figures, panels, tags and biological entities:

![data model](sd-graph-data-model.png) 

As a last step, genes and proteins have to be mapped to each other. First, go in the neo4j client in your browser and run this CYPHER command to extract all the Uniprot identifiers:

    MATCH (t:Tag)
    WHERE t.type = "protein" AND t.ext_id <> ""
    WITH split(t.ext_id,"///") AS ids
    UNWIND ids as id
    RETURN DISTINCT id

Save the results as csv file (for example to a `export.csv`). Go to http://www.uniprot.org/uploadlists/ and upload this file to generate a `UniProtKB AC/ID` to `GeneID (Entrez Gene)` mapping `protein2gene.tab` file (select the "mapping table" format).

Move the `protein2gene.tab` into the `neo4j/import/` directory (this is set in `neo4j.conf` as the default directory for importing files) and build the protein-to-gene mapping with

    neo4j-shell -file SD-protein2gene.cql
 
Et voilà!

The database is now ready and the examples provided in SD-scripts can then be run directly in the neo4j browser client.
