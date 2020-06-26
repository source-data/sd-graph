<template lang="pug">
  div
    el-row
        el-col(:span="16" :offset="4")
          p
           b The <i>Early Evidence Base</i> (EEB) platform is an experimental resource that combines computer automation with human expertise to highlight scientific results from preprints.

          p Preprints provide the scientific community with early access to scientific evidence. 
            | For experts, this communication channel is an efficient way to mutually benefit from the research shared by colleagues and has therefore the potential to accelerate scientific progress. 
          
          p For non-experts, navigating preprints can be challenging: in absence of peer-review, interpreting the data, evaluating the quality of the results and the strength of the conclusions is often impossible; finding specific and relevant information in the rapidly accumulating corpus of preprints is increasingly difficult.

          p The current COVID-19 pandemic has made this tradeoff even more visible. 
            | The urgency in understanding and combatting SARS-CoV-2 viral infection has stimulated an unprecedented rate of preprint posting. 
            | It has however also revealed the risk associated with misinterpretating preliminary results shared in preprint and the confusion that may result from premature amplification of early results by non-experts or the media.

          p To experiment with ways in which technology and human expertise can be combined to address these issues, EMBO has built the EEB. The platform prioritizes 
            | <el-link type="primary" href="https://biorxiv.org"><i>bioRxiv</i></el-link> preprints in three complementary ways:
            ul 
              li Refereed Preprints are preprints that are associated with reviews. EEB prioritizes such preprints and integrates the content of the reviews as well as the authors' response, when available, to provide rich context and in-depth analyses of the reported research. Note that the reviews from Review Commons are not linked to any journals and are obtained before journal submission. 
              li To highlight the importance of experimental evidence, EEB automatically prioritizes recent preprints related to the biology of SARS-CoV-2 based on hypothesis-driven experimentation reported in the figures of preprints. 
              li Finally, EEB provides a selection of preprints that are enriched for studies that use a diversity of experimental approaches.

          p The platform combines the following technologies:
            ul
              li The standardized MECA/JATS archive provided by <i>bioRxiv</i> are parsed and converted into a graph before loading and indexing into a <el-link type="primary" href="https://neo4j.com">neo4j</el-link> graph database. 
                | EEB does not intend to reproduce the full content of the preprints which are best accessed from the bioRixv site.
              li The reviews produced by <el-link type="primary" href="https://reviewcommons.org"><i>Review Commons</i></el-link>, <el-link type="primary" href="https://elifesciences.org/"><i>eLife</i></el-link> 
                | and <el-link type="primary" href="https://embopress.org"><i>EMBO Press</i></el-link> that are posted on bioRxiv are integrated into EEB. 
                | We use the <el-link type="primary" href="https://github.com/embo-press/hypothepy">hypothepy</el-link> python binding to the <el-link type="primary" href="https://hypothes.is/">hypothes.is</el-link> API 
                | and <el-link type="primary" href="https://github.com/embo-press/traxiv">traxiv</el-link> automated linking of EMBO Press transparent reviews.
              li The content of figure legends is analyzed with the SmartTag deep learning engine to extract potential hypotheses experimentally tested 
                | and to identify experimental approaches used in preprints.
              li The database is a <el-link type="primary" href="https://neo4j.com">neo4j</el-link> graph database that naaturally lends itself to the kind of network-based queries used in this application.
              li The <el-link type="primary" href="https://sourcedata.io">SourceData</el-link> compendium of manually annotated experiment is used to train the SmartTag engine and to cluster synonyms using a network-based approach.
              li The platform is run on the cloud using <el-link type="primary" href="https://www.docker.com/">Docker</el-link> containers to virtualize its environment and make it more easily portable.

          p EEB is under development and is run as an experiment to push boundaries scientific publishing. Please send us your thoughts, suggestions and feedback to: 
            el-link(href="mailto:sourcedata@embo.org" type="primary") sourcedata@embo.org
    </template>
