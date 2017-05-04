from sdapi import SDAPI
import sys
import argparse
from neo4jrestclient.client import GraphDatabase, Node, Relationship

#Amazon: http://34.202.28.116:7474/db/data
#password = the project on amazon...
#passwrod = classic publishing on local

DEBUG_MODE = False

class SD_neo():

    @staticmethod
    def create_graph(name, years=range(1997, 2016+1)):
        N = 0
        skipped = 0
        collection = SDAPI.request_collection(name=name)
        collection_id = collection.id
        article_list = SDAPI.request_article_list(collection_id)
        doi_list = article_list.doi_list
        total = str(len(doi_list))
        print "collection " + collection_id + " contains " + total + " papers with a DOI."   
        for doi in doi_list:
           if not doi:
               print "Skipping empty doi"
               skipped+=1
           else:
               print "Trying paper {}".format(doi)
               a = SDAPI.request_article(doi, collection_id)
               if not a.data:
                   print "no data in " + doi
               else:
                   #problem if article already exists
                   try:
                       article_node = a.node(DB, collection.name)
                       N+=1
                       print doi +" has " + str(a.nb_figures) + " figures"
                       for i in range(1, a.nb_figures+1):
                          f = SDAPI.request_figure(doi, collection_id, figure_order=i)
                          if f.data:
                              figure_node = f.node(DB, collection.name)
                              if f.data:
                                  article_node.relationships.create("has_figure", figure_node)
                                  N+=1
              
                                  for panel_id in f.panels:
                                     if panel_id:
                                         print "    Trying panel {}".format(panel_id)
                                         p = SDAPI.request_panel(panel_id)
                                         if p.data:  
                                             panel_node = p.node(DB, collection.name)
                                             figure_node.relationships.create("has_panel", panel_node)
                                             N+=1
                 
                                             for category in ['assay', 'entities', 'time', 'physical']:
                                         
                                                 for t in p.tags[category]:
                                                     #print "cypher: ", t._cypher_create()
                                                     tag_node = t.node(DB, collection.name)
                                                     panel_node.relationships.create("has_tag", tag_node)
                                                     N+=1
                   except Exception as e:
                      print e

        return total, skipped, N
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser( description="Uploads collection to neo4j datatbase" )
    parser.add_argument('collections', help="Comma-separated name(s) of the collection(s) to download")
    parser.add_argument( '-y', '--years', default='1997:2016', help='Year range to download (default: %(default))' )
    parser.add_argument('-u', '--username', default='neo4j', help='username to connect to neo4j')
    parser.add_argument('-p', '--password', default='', help='password to connect to neo4j')
    parser.add_argument('-H', '--host', default='http://localhost:7474/db/data/', help='url to access neo4j')

    args = parser.parse_args()

    collections = args.collections.split(',')
    y = args.years.split(":")
    years = range(int(y[0]),int(y[1])+1)
    username = args.username
    password = args.password
    url = args.host
    
    DB = GraphDatabase(url, username=username, password=password)
    print("Importing"+", ".join(collections))
    for collection in collections:
         collection = collection.strip()
         total, skipped, N = SD_neo.create_graph(collection, years=years)
         print "created: {} nodes from {} papers (skipped: {}) for collection {}".format(N, total, skipped, collection)
    

