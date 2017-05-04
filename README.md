# sd-graph
(Source Data)[http://sourcedata.embo.org)
We provide here the scripts required to build the SourceData sd-graph database in neo4j and examples of analyses. 
When refering to SourceData, please cite the following paper:

Install the neo4j database according to the instructions provided at http://neo4j.com
(the scripts were tested under neo4j 2.2)
To download the content of the SourceData database through the SourceData API and populate the neo4j database, run this command:

    python sdneo.py --password <your_password_to_your_neo4j_instance> PUBLICSEARCH
  
Next, build the relationships to create the sd-graph model:

    neo4j-shell -file SD-constraints.cql
    neo4j-shell -file SD-processing.cql

This will create the following model:

Finally, we need to create a protein to gene mapping. First, go in the neo4j client in your browser and run this CYPHER command:

    MATCH (t:Tag)
    WHERE t.type = "protein" AND t.ext_id <> ""
    WITH split(t.ext_id,"///") AS ids
    UNWIND ids as id
    RETURN DISTINCT id

Save the results as csv to a file export.csv
Go to http://www.uniprot.org/uploadlists/ and generate a `UniProtKB AC/ID` to `GeneID (Entrez Gene)` mapping protein2gene.tab
To upload this file and build the protein to gene mapping run

    neo4j-shell SD-protein2gene.cql
 
Et voilà!

The examples provided in SD-scripts can then be run directly in the neo4j client.
