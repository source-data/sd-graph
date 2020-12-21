<template lang="pug">
  v-container
    p The platform integrates multiple technologies:
      ul
        li
          | The standardized MECA/JATS archives provided by <a target="_blank" rel="noopener" href="https://biorxiv.org"><i>bioRxiv</i></a> and the <a target="_blank" rel="noopener" href="https://api.biorxiv.org">bioRxiv API</a> are used to populate the EEB database.
          | Note that EEB does not intend to reproduce the full content of the preprints which are best accessed from the <a target="_blank" rel="noopener" href="https://biorxiv.org"><i>bioRxiv</i></a> and <a target="_blank" rel="noopener" href="https://medRxiv.org"><i>medRxiv</i></a> sites.
        li 
          | The reviews produced by <a target="_blank" rel="noopener" href="https://reviewcommons.org"><i>Review Commons</i></a>, <a target="_blank" rel="noopener" href="https://elifesciences.org/"><i>eLife</i></a>, <a target="_blank" rel="noopener" href="https://embopress.org"><i>EMBO Press</i></a> are integrated using the <a target="_blank" rel="noopener" href="https://github.com/embo-press/hypothepy">hypothepy</a> python binding to the <a target="_blank" rel="noopener" href="https://hypothes.is/">hypothes.is</a> API.
          | The reviews produced by <a target="_blank" rel="noopener" href="https://rapidreviewscovid19.mitpress.mit.edu/"><i>Rapid Reviews: COVID-19</i></a> and <a target="_blank" rel="noopener" href="https://peercommunityin.org/"><i>Peer Community In</i></a> are integrated using the <a target="_blank" rel="noopener" href="https://crossref.org/">CrossRef</a> API.
        li 
          | The content of figure legends is analyzed with the <a target="_blank" rel="noopener" href="https://github.com/source-data/py-smtag">SmartTag</a> deep learning engine to extract potential hypotheses experimentally tested and to identify experimental approaches used in preprints.
        li 
          | The <a target="_blank" rel="noopener" href="https://sourcedata.io">SourceData</a> compendium of manually annotated experiment is used to train the SmartTag engine and to cluster synonyms using a network-based approach.
        li
          | The knowledge graph extracted from figure legends is stored in a <a target="_blank" rel="noopener" href="https://neo4j.org">neo4j</a> database to facilitate subsequent analysis with graph data science algorithms.
        li
          | The platform is run on the cloud using <a target="_blank" rel="noopener" href="https://www.docker.com/">Docker</a> containers to virtualize its environment and simplify deployment.
</template>