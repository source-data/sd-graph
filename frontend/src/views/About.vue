<template lang="pug">
  div
    el-row
        el-col(:span="18" :offset="2")
          p
           b The <i>Early Evidence Base</i> (EEB) platform is an experimental resource that combines computer automation with human expertise to highlight scientific results from preprints.

          p Preprints provide the scientific community with early access to scientific evidence. 
            | For experts, this communication channel is an efficient way to accesss research without delay and thus to accelerate scientific progress. 
          
          p For non-experts, navigating preprints can be challenging: in absence of peer-review and journal certification, interpreting the data, evaluating the quality of the results and the strength of the conclusions is often impossible; finding specific and relevant information in the rapidly accumulating corpus of preprints is becoming increasingly difficult.

          p The current COVID-19 pandemic has made this tradeoff even more visible. 
            | The urgency in understanding and combatting SARS-CoV-2 viral infection has stimulated an unprecedented rate of preprint posting. 
            | It has however also revealed the risk resulting from misinterpretation of preliminary results shared in preprint and with amplification or perpetuating prelimature claims by non-experts or the media.

          p To experiment with ways in which technology and human expertise can be combined to address these issues, EMBO has built the EEB. The platform prioritizes 
            | <el-link type="primary" href="https://biorxiv.org"><i>bioRxiv</i></el-link> preprints in complementary ways:
            ul 
              li Refereed Preprints are preprints that are associated with reviews. EEB prioritizes such preprints and integrates the content of the reviews as well as the authors' response, when available, to provide rich context and in-depth analyses of the reported research. Note that the reviews from Review Commons are not linked to any journals and are obtained before journal submission. 
              li To highlight the importance of experimental evidence, EEB automatically prioritizes recent preprints related to the biology of SARS-CoV-2 based on hypothesis-driven experimentation reported in the figures of preprints. 
              li Finally, EEB provides a selection of preprints that are enriched for studies that use a diversity of experimental approaches.

          p The platform integrates multiple technologies:
            ul
              li The standardized MECA/JATS archive provided by <i>bioRxiv</i> are parsed and loaded in a graph database that naturally lends itself to the kind of network-based queries used in this application. 
                | EEB does not intend to reproduce the full content of the preprints which are best accessed from the <el-link type="primary" href="https://biorxiv.org"><i>bioRxiv</i></el-link> site.
              li The reviews produced by <el-link type="primary" href="https://reviewcommons.org"><i>Review Commons</i></el-link>, <el-link type="primary" href="https://elifesciences.org/"><i>eLife</i></el-link> 
                | and <el-link type="primary" href="https://embopress.org"><i>EMBO Press</i></el-link> that are posted on bioRxiv are integrated into EEB. 
                | We use the <el-link type="primary" href="https://github.com/embo-press/hypothepy">hypothepy</el-link> python binding to the <el-link type="primary" href="https://hypothes.is/">hypothes.is</el-link> API 
                | and <el-link type="primary" href="https://github.com/embo-press/traxiv">traxiv</el-link> automated linking of EMBO Press transparent reviews.
              li The content of figure legends is analyzed with the <el-link type="primary" href="https://github.com/source-data/py-smtag">SmartTag</el-link> deep learning engine to extract potential hypotheses experimentally tested 
                | and to identify experimental approaches used in preprints.
              li The <el-link type="primary" href="https://sourcedata.io">SourceData</el-link> compendium of manually annotated experiment is used to train the SmartTag engine and to cluster synonyms using a network-based approach.
              li The platform is run on the cloud using <el-link type="primary" href="https://www.docker.com/">Docker</el-link> containers to virtualize its environment and simplify deployment.

          p EEB is under development and is run as an experiment to push boundaries scientific publishing. Please send us your thoughts, suggestions and feedback to: 
            el-link(href="mailto:sourcedata@embo.org" type="primary") sourcedata@embo.org
    </template>
