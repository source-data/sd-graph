#!/usr/bin/python
from sdapi import SDAPI
import argparse
import os
from dotenv import load_dotenv
from neo4jrestclient.client import GraphDatabase, Node, Relationship


class SD_neo():

    @staticmethod
    def create_graph(name, years, username_sdapi, password_sdapi):
        N = 0
        skipped = 0
        sdapi = SDAPI()
        sdapi.usr = username_sdapi
        sdapi.pswd = password_sdapi
        collection = sdapi.request_collection(name=name)
        collection_id = collection.id
        article_list = sdapi.request_article_list(collection_id)
        doi_list = article_list.doi_list
        total = str(len(doi_list))
        print("collection " + collection_id + " contains " + total + " papers with a DOI.")  
        for doi in doi_list:
           if not doi:
               print("Skipping empty doi")
               skipped+=1
           else:
               print("Trying paper {}".format(doi))
               a = sdapi.request_article(doi, collection_id)
               if not a.data:
                   print("no data in " + doi)
               else:
                   #problem if article already exists
                   try:
                       article_node = a.node(DB, collection.name)
                       N+=1
                       print(doi +" has " + str(a.nb_figures) + " figures")
                       for i in range(1, a.nb_figures+1):
                          f = sdapi.request_figure(doi, collection_id, figure_order=i)
                          if f.data:
                              figure_node = f.node(DB, collection.name)
                              if f.data:
                                  article_node.relationships.create("has_figure", figure_node)
                                  N+=1
              
                                  for panel_id in f.panels:
                                     if panel_id:
                                         print("    Trying panel {}".format(panel_id))
                                         p = sdapi.request_panel(panel_id)
                                         if p.data:  
                                             panel_node = p.node(DB, collection.name)
                                             figure_node.relationships.create("has_panel", panel_node)
                                             N+=1
                 
                                             for category in ['assay', 'entities', 'time', 'physical']:
                                         
                                                 for t in p.tags[category]:
                                                     tag_node = t.node(DB, collection.name)
                                                     panel_node.relationships.create("has_tag", tag_node)
                                                     N+=1
                   except Exception as e:
                      print(e)
                      raise

        return total, skipped, N
    
if __name__ == "__main__":
    load_dotenv()
    URI = os.getenv('NEo_URI')
    NEO_USERNAME = os.getenv("NEO_USERNAME")
    NEO_PASSWORD = os.getenv("NEO_PASSWORD")
    SD_API_USERNAME = os.getenv("SD_API_USERNAME")
    SD_API_PASSWORD = os.getenv("SD_API_PASSWORD")

    parser = argparse.ArgumentParser( description="Uploads collection to neo4j datatbase" )
    parser.add_argument('collections', help="Comma-separated name(s) of the collection(s) to download")
    parser.add_argument( '-y', '--years', default='1997:2018', help='Year range to download (default: %(default))' )
    parser.add_argument('-u', '--username', default=NEO_USERNAME, help='username to connect to neo4j')
    parser.add_argument('-p', '--password', default=NEO_PASSWORD, help='password to connect to neo4j')
    parser.add_argument('-H', '--host', default='http://localhost:7474/db/data/', help='url to access neo4j')
    parser.add_argument('-U', '--username_sdapi', default=SD_API_USERNAME, help='username to connect to sourcedata api')
    parser.add_argument('-P', '--password_sdapi', default=SD_API_PASSWORD, help='password to connect to sourcedata api')
    
    # usage: python -m sdneo Sars-CoV-2 -u neo4j -p sourcedata -U sourcedata_api_username -P sourcedata_api_password

    args = parser.parse_args()

    collections = args.collections.split(',')
    y = args.years.split(":")
    years = range(int(y[0]),int(y[1])+1)
    username = args.username
    password = args.password
    username_sdapi = args.username_sdapi
    password_sdapi = args.password_sdapi
    url = args.host
    
    DB = GraphDatabase(url, username=username, password=password)
    print("Importing: "+", ".join(collections))
    for collection in collections:
         collection = collection.strip()
         total, skipped, N = SD_neo.create_graph(collection, years, username_sdapi, password_sdapi)
         print("created: {} nodes from {} papers (skipped: {}) for collection {}".format(N, total, skipped, collection))
    

