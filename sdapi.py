#!/usr/bin/python
import requests
import argparse
import re
import htmlentitydefs
from neo4jrestclient.client import GraphDatabase,Node,Relationship

REST_API    = "https://api.sourcedata.io/"

GET_COLLECTION = "collection/"
GET_LIST    = "papers"
GET_ARTICLE = "paper/"
GET_FIGURE  = "figure/"
GET_PANEL   = "panel/"

class Util():
    @staticmethod
    def rest2data(url, usr, pswd):
        data = dict()
        #print "API request: ", url
        try:
            response = requests.get(url, auth=(usr, pswd))
            #print "server response: ", response.text, usr, pswd
            try: 
                data = response.json()
            except Exception as e:
                print "WARNING: problem with loading json object with %s" % url
                print type(e), e
                print response.json()
        except Exception as e:
            print "failed to get response from server"
            print type(e), e
        finally:
            if data is not None:
                return data
            else:
                print "response is empty"
                return dict()
                
    @staticmethod
    def quote4neo(attributes):
        quotes_added = {k:'"{}"'.format(v.encode('utf-8').replace("'",r"\'").replace('"',r'\"')) if isinstance(v, basestring) else v for k,v in attributes.items()}
        #include some cleanup of HTML entities eg &nbsp;
        properties = ','.join(["{}:{}".format(k,v) for (k,v) in quotes_added.items()])
        return properties

class SD_item(object):
    
    verbose = False
    
    def item_print(self):
        for k in self.data: 
           print k,":", self.data[k]
    
    def _cypher_create(self,db):
        return ""
          
    def node(self, neo4j_db, collection = ''):
        set_collection = " SET n.collection = \"{}\" ".format(collection) if collection else ''
        q = self._cypher_create() + set_collection + " RETURN n"
        self.neo = neo4j_db.query(q, returns = Node)[0][0]
        return self.neo
          
    def __init__(self, url, usr, pswd):
        if self.verbose: print url
        data = Util.rest2data(url, usr, pswd)
        self.data = data


class SD_collection(SD_item):

    def _set_id(self):
        self.id = self.data[0]['collection_id']
        
    def _set_name(self):
        self.name = self.data[0]['name']
    
    def __init__(self, url, usr, pswd):
        super(SD_collection, self).__init__(url, usr, pswd)
        self._set_id()
        self._set_name()


class SD_article_list(SD_item):

    def _set_doi_list(self):
        self.doi_list = [a['doi'] for a in self.data]
        
    def _set_title_list(self):
        self.title_list = [a['title'] for a in self.data]
        
    def _set_title_doi_dictionary(self):
        self.title_doi_dictionary = {a['id']:{"title":a['title'], "doi":a['doi']} for a in self.data}
    
    def item_print(self):
        ", ".join([doi for doi in self.doi_list])
    
    def __init__(self, url, usr, pswd):
        super(SD_article_list, self).__init__(url, usr, pswd)
        self.doi_list = []
        self._set_doi_list()
        self._set_title_list()
        self._set_title_doi_dictionary()

class SD_article(SD_item):
    def _set_title(self):
        self.title = ""
        if 'title' in self.data:
            self.title = self.data['title'] or ''
            
    def _set_journal(self):
        self.journal = ""
        if 'journal' in self.data:
            self.journal = self.data['journal'] or ''           
            
    def _set_year(self):
        self.year = ""
        if 'year' in self.data:
            self.year = self.data['year'] or ''
            
    def _set_doi(self):
        self.doi = ""
        if 'doi' in self.data:
            self.doi = self.data['doi'] or ''
            
    def _set_pmid(self):
        self.pmid = ""
        if 'pmid' in self.data:
            self.pmid = self.data['pmid'] or ''
       
    def _set_nb_figures(self):
        self.nb_figures = 0
        if 'nbFigures' in self.data:
            if self.data['nbFigures'] is not None: self.nb_figures = int(self.data['nbFigures']) 
    
    def _cypher_create(self):
        # need to use Util.quote4neo to avoid problems with ' and " in text
        attributes = Util.quote4neo({'doi':self.doi, 'pmid':self.pmid, 'title':self.title, 'journalName':self.journal, 'year':self.year})
        return 'CREATE (n:Article {{ {} }})'.format(attributes)
               
    def __init__(self, url, usr, pswd):
        super(SD_article, self).__init__(url, usr, pswd)
        self._set_title()
        self._set_journal()
        self._set_year()
        self._set_doi()
        self._set_pmid()
        self._set_nb_figures()
    

class SD_figure(SD_item):
    def _set_label(self):
        self.label = ""
        if 'label' in self.data:
           self.label = self.data['label'] or ''
           
    def _set_caption(self):
        self.caption = ""
        if 'caption' in self.data:
           self.caption = self.data['caption'] or ''

    def _set_href(self):
        self.href = ""
        if 'href' in self.data:
           self.href = self.data['href'] or ''

    def _set_panels(self):
        self.panels = []
        if 'panels' in self.data:
            self.panels = self.data['panels'] or []
            
            
    def _cypher_create(self):
        attributes = Util.quote4neo({'fig_label':self.label, 'caption':self.caption, 'href': self.href})
        return 'CREATE (n:Figure {{ {} }})'.format(attributes)
        
    def __init__(self, url, usr, pswd):
        super(SD_figure, self).__init__(url, usr, pswd)
        
        self._set_caption()
        self._set_label()
        self._set_href()
        self._set_panels()        

class SD_panel(SD_item):

    def _set_me(self):
         panels = self.data['figure']['panels']
         #fancy generator expression to find current panel which is provided in a list and not in a dictionary :-(
         self.me = (p for p in panels if p['panel_id']==self.id).next()

    def _set_id(self):
         self.id = self.data['current_panel_id']
         
    def _set_label(self):
         self.label = ""
         if 'label' in self.me:
             self.label = self.me['label'] or ''
             
    def _set_caption(self):
         self.caption = ""
         if 'caption' in self.me:
             self.caption = self.me['caption'] or ''
             
    def _set_formatted_caption(self):
         self.formatted_captionn = ""
         if 'formatted_caption' in self.me:
             self.formatted_caption = self.me['formatted_caption'] or ''
             
    def _set_href(self):
         self.href = ""
         if 'href' in self.me:
             self.href = self.me['href'] or ''
             
    
    def _set_coords(self):
         self.coord = ""
         if 'coords' in self.me:
             coords = self.me['coords']
             self.coords = ", ".join(["{}={}".format(c,coords[c]) for c in coords]) 
    
    def _set_tags(self):
         self.tags = dict()
         if 'tags' in self.me:
             tags = self.me['tags']
             for category in ['assay','time', 'physical']:
                 self.tags[category] = [SD_tag(t) for t in tags if t['category'] == category]
             #by convention, entities are assigned an empty category attribute
             self.tags['entities'] = [SD_tag(t) for t in tags if t['category'] is None]
         else:
             for c in ['entities', 'assay','time', 'physical']: self.tags[c] = [] 
    
    def _set_assay(self):
         #what if no tags['assay']?
         self.assays = "///".join([t.text for t in self.tags['assay']])
         
    def _cypher_create(self):
        attributes = Util.quote4neo({"panel_id":self.id, "label":self.label, "caption":self.caption, 
        "formatted_caption":self.formatted_caption, 
        "coords":self.coords, "href":self.href}) 
        return "CREATE (n:Panel {{ {} }})".format(attributes)

        
    def __init__(self, url, usr, pswd):
        super(SD_panel, self).__init__(url, usr, pswd)
        self._set_id()
        self._set_me()
        self._set_href()
        self._set_label()
        self._set_caption()
        self._set_formatted_caption()
        self._set_coords()
        self._set_tags()
        self._set_assay()
            
class SD_tag(SD_item):
    
    def _set_tag_id(self):
        self.id = ''
        if 'id' in self.data:
            self.id = self.data['id'] or ''
    
    def _set_category(self):
        self.category = ''
        if 'category' in self.data:
            self.category = self.data['category'] or ''
           
    def _set_type(self):
        self.type = ""
        if 'type' in self.data:
            self.type = self.data['type'] or ''
           
    def _set_role(self):
        self.role = ""
        if 'role' in self.data:
            self.role = self.data['role'] or ''
           
    def _set_text(self):
        self.text = ""
        if 'text' in self.data:
            self.text = self.data['text'] or ''
           
    def _set_ext_ids(self):
        self.ext_ids = ""
        if 'external_ids' in self.data:
            if self.data['external_ids'] is not None: self.ext_ids = "///".join(self.data['external_ids'])
   
    def _set_ext_dbs(self):
        self.ext_dbs = ""
        if 'external_databases' in self.data:
            if self.data['external_databases'] is not None: self.ext_dbs = "///".join(self.data['external_databases']) 
           
    def _set_in_caption(self):
        self.in_caption = False
        if 'in_caption' in self.data:
            if self.data['in_caption'] is not None: self.in_caption = self.data['in_caption'] == "Y" 
            
    def _set_ext_names(self):
        self.ext_names = ""
        if 'external_names' in self.data:
            if self.data['external_names'] is not None: self.ext_names = "///".join(self.data['external_names'])
           
    def _set_tax_ids(self):
        self.ext_tax_ids = ""
        if 'external_tax_ids' in self.data:
            if self.data['external_tax_ids'] is not None: self.ext_tax_ids = "///".join(self.data['external_tax_ids'])   
           
    def _set_tax_names(self):
        self.ext_tax_names = ""
        #change filed to external_names
        if 'external_tax_names' in self.data:
            if self.data['external_tax_names'] is not None: self.ext_tax_names = "///".join(self.data['external_tax_names'])
           
    def _set_ext_urls(self):
        self.ext_urls = ""
        if 'ext_urls' in self.data:
            if self.data['external_urls'] is not None: self.ext_urls = "///".join(self.data['external_urls'])
           
    def _cypher_create(self):
        attributes = Util.quote4neo({'id':self.id,
                                     'category':self.category, 'type':self.type, 
                                     'role':self.role, 'text':self.text, 
                                     'ext_id':self.ext_ids, 'ext_dbs':self.ext_dbs, 
                                     'in_caption':self.in_caption, 'ext_names':self.ext_names, 
                                     'tax_names':self.ext_tax_names, 'tax_id':self.ext_tax_ids, 
                                     'ext_urls':self.ext_urls})
        #add external_names and externl_tax_ids 
        return 'CREATE (n:Tag {{ {} }})'.format(attributes)
        
    def __init__(self, tag_data):
        self.data = tag_data
        self._set_tag_id()
        self._set_category()
        self._set_type()
        self._set_role()
        self._set_text()
        self._set_in_caption()
        self._set_ext_names()
        self._set_ext_ids()
        self._set_ext_dbs()
        self._set_tax_ids()
        self._set_tax_names()
        self._set_ext_urls()

class SDAPI():  
    
    @property
    def usr(self):
        return self._usr
    
    @usr.setter
    def usr(self, usr = ''):
        self._usr = usr
        
    @property
    def pswd(self):
        return self._pswd
    
    @pswd.setter
    def usr(self, pswd = ''):
        self._pswd = pswd
    
    def request_collection(self, name ="PUBLICSEARCH"):
        url = REST_API + GET_COLLECTION + name
        collection = SD_collection(url, self.usr, self.pswd)
        return collection
    
    def request_article_list(self, collection_id):
        url = REST_API + GET_COLLECTION + collection_id + "/" + GET_LIST
        article_list = SD_article_list(url, self.usr, self.pswd)
        return article_list
    
    def request_article(self, doi, collection_id):
        url = REST_API + GET_COLLECTION + collection_id + "/" + GET_ARTICLE+doi
        article = SD_article(url, self.usr, self.pswd)
        return article
            
    def request_figure(self, doi, collection_id, figure_order=1):
        url = REST_API + GET_COLLECTION + collection_id +"/" + GET_ARTICLE + doi + "/" + GET_FIGURE + str(figure_order)
        figure = SD_figure(url, self.usr, self.pswd)
        return figure

    def request_panel(self, id):
        url = REST_API + GET_PANEL + id
        panel = SD_panel(url, self.usr, self.pswd)
        return panel
    
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser( description="interace to the SourceData API" )
    parser.add_argument('-C', '--collection', default="", help="Takes the name of a collection (try \"PUBLICSEARCH\") nd returns the list of papers")
    parser.add_argument('-I', '--collection_id', default="", help="Takes the id of a collection (try \"97\") and returns the list of papers")
    parser.add_argument('-D', '--doi', default = '', help="Takes a doi and return article information")
    parser.add_argument('-F', '--figure', default = '', help="Takes the figure index and returns the figure legend for the figure in the paper specified with the --doi option") 
    parser.add_argument('-P', '--panel', default='', help="Takes the id of a panel and returns the tagged text of the legend")
    parser.add_argument('-u', '--username', default='', help='username to connect to the SourceData API; not necessary for accessing the public collection PUBLICSEARCH')
    parser.add_argument('-p', '--password', default='', help='password to connect to the SourceData API; not necessary for accessing the public collection PUBLICSEARCH')
    parser.add_argument('-v', '--verbose', action='store_const', const=True, default=False , help='verbose mode')
    
    args = parser.parse_args()

    collection_name = args.collection
    collection_id = args.collection_id
    doi = args.doi
    fig = args.figure
    panel_id = args.panel
    usr = args.username
    pswd = args.password
    
    SD_item.verbose = args.verbose
    
    sdapi = SDAPI()
    sdapi.usr = usr
    sdapi.pswd = pswd
    
    default_collection_id = sdapi.request_collection("PUBLICSEARCH").id
    print "default collection id = {}".format(default_collection_id) 
    if collection_name:
        c = sdapi.request_collection(collection_name) 
        print "collection id = {}".format(c.id)
        article_list = sdapi.request_article_list(c.id)
        title_doi_dictionary = article_list.title_doi_dictionary
        for id in title_doi_dictionary:
            print title_doi_dictionary[id]['doi'], title_doi_dictionary[id]['title']
            
    if collection_id:
        article_list = sdapi.request_article_list(collection_id)
        print len(article_list.doi_list), len(article_list.title_list), len(article_list.title_doi_dictionary)
        counter = 1
        for doi in article_list.doi_list:
            print counter, doi
            counter += 1
            
    if doi: 
        article = sdapi.request_article(doi, default_collection_id)
        print 'doi:', article.doi
        print 'title:', article.title
        print 'journal:', article.journal
        print 'year:', article.year
        print 'pmid:', article.pmid
        print 'number of figures:', article.nb_figures
        
    if fig:
        figure = sdapi.request_figure(doi, default_collection_id, fig)
        print "label:", figure.label
        print "caption:", figure.caption
        print "url:", figure.href
        print "panel ids:", "\t".join(figure.panels)
        
    if panel_id:
        panel = sdapi.request_panel(panel_id)
        print "label:", panel.label
        print "url:", panel.href
        print "caption:", panel.caption
        print
        print "formatted caption:", panel.formatted_caption
        print "coordinates:", panel.coords
        for category in panel.tags:
           print
           print "Tag category: ", category
           for t in panel.tags[category]:
               print u'"{}"[{}:{}] {} {} {} tag id={}'.format(t.text,t.ext_dbs, t.ext_ids, t.role, t.type, 'in_caption' if t.in_caption else 'floating tag', t.id)
               

        
         