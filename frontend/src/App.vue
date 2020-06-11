<template lang="pug">
  el-container
    el-header(height="200px")#header
      el-col(:span="4")
        div.vertical-align
          p
            a(href="https://embo.org" target="_blank" )
              img(src="./assets/embo-logo.gif" height="80px").center-img
      el-col(:span="16")
        div.vertical-align
          h1(style="text-align: center") Early Evidence Base - Refereed Preprints
      el-col(:span="4")
        div.vertical-align
          p 
            a(href="https://sourcedata.io" target="_blank" )
              img(src="./assets/sourcedata-logo.png" width="200px").center-img
          p
            a(href="https://embopress.org")
              img(src="./assets/embopress-logo.jpg" width="200px").center-img
    el-container
      el-aside(width="170px" style="border-right-style: solid; border-right-width: 1px; padding-top: 50px")
        p.side_bar_links
          el-link(href="") About
        p.side_bar_links
          el-link(href="") For developers
        p.side_bar_links
          el-link(href="") Contact
        el-divider
        
        small Database stats: 
          p 
            code {{ db_stats.ai_annotated || 0 }}
            |  preprints automatically annotated. 
          p 
            code {{ db_stats.sd_annotated || 0 }}
            |  experiments in the SourceData knowledge graph
          p 
            code {{db_stats.total_nodes || 0 }}
            |  nodes in EBB.

      el-main
        el-row
          el-col(:span="16" :offset="4")
            p The Early Evidence Base (EEB) is an experimental platform
              |  that  combines artificial intelligence with human curation 
              |  and expert peer-review to highlight results posted in 
              el-link(type="primary" href="https://biorxiv.org") bioRxiv
              |  preprints. 
            p The EEB platform is a technology experiment developed by  
              el-link(type="primary" href="https://embopress.org") EMBO Press.
              
            p EEB builds upon the full-text content provided by bioRxiv in the form of standardized structured MECA/JATS archives.
              |  It uses the SmartTag engine for semantic text analysis of figure legends and the 
              el-link(type="primary"  href="https://sourcedata.io") SourceData 
              |  knowledge graph of manually curated experiments.
              | Taking advantage of the 
              el-link(type="primary" href="https://www.cshl.edu/transparent-review-in-preprints/") TRiP 
              |  and 
              el-link(type="primary" href="https://hypothes.is/") hypothes.is 
              |  technologies and EMBO Press 
              el-link(type="primary" href="https://github.com/embo-press/hypothepy") hypothepy 
              |  and 
              el-link(type="primary" href="https://github.com/embo-press/traxiv" ) traxiv 
              |  automatic linking, public peer reviews posted as Refereed Preprints by 
              el-link(type="primary" href="https://reviewcommons.org/refereed-preprints") Review Commons 
              |  as well as peer reviews linked by 
              el-link(type="primary" href="https://embopress.org") EMBO Press
              |  and posted by 
              el-link(type="primary" href="https://elifesciences.org") eLife 
              |  are directly accessible.
        el-row
          el-col(:span="16" :offset="4")
            SearchBar
        el-row
          el-col(:span="16" :offset="4")
            QuickAccess
        el-row
          el-col(:span="16" :offset="4")
            Highlights
    el-footer
      el-row
        el-col(:span="16" :offset="4")
          small EMBO 	&#169; {{ thisYear }}

</template>

<script>
import { mapGetters } from 'vuex'
import SearchBar from './components/search-bar.vue'
import QuickAccess from './components/quick-access/index.vue'
import Highlights from './components/highlights/index.vue'

export default {
  name: 'app',
  components: {
    SearchBar,
    QuickAccess,
    Highlights,
  },
  computed: {
    thisYear () {
      return new Date().getFullYear()
    },
    ...mapGetters(['db_stats'])
  },
  beforeCreate () {
    this.$store.dispatch('byReviewingService/getAll'),
    //this.$store.dispatch('byMethod/getAll'),
    //this.$store.dispatch('byMol/getAll'),
    this.$store.dispatch('byHyp/getAll'),
    this.$store.dispatch('byAutomagic/getAll')
    this.$store.dispatch('statsFromFlask')
  },
}
</script>

<style scoped lang="scss">
#header {
   border-bottom-style: solid;
   border-bottom-width: 1px;
}

img.center-img {
  display: block;
  margin-left: auto;
  margin-right: auto;
}

.vertical-align {
  margin-top: 80px;
  transform: translate(0, -50%) 
}

.side_bar_links {
  padding-left: 25px;
}
</style>


