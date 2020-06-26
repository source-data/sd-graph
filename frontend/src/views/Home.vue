<template lang="pug">
  div
    el-row
      el-col(:span="20" :offset="2")
        p <i>Early Evidence Base</i> (EEB) is an <b>experimental platform</b>
          |  that  combines artificial intelligence with human curation 
          |  and expert peer-review to highlight results posted in 
          el-link(type="primary" href="https://biorxiv.org") bioRxiv
          |  preprints. 
        p The EEB platform is a technology experiment developed by  
          el-link(type="primary" href="https://embopress.org") EMBO Press.
          
        p EEB automatically indexes and prioritizes <i>bioRixv</i> preprints by parsing the full-text MECA/JATS archives provided by <i>bioRxiv</i>.
          | It uses the SmartTag engine for semantic text analysis of figure legends and the 
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
      el-col(:span="20" :offset="2")
        SearchBar
    el-row
      el-col(:span="20" :offset="2")
        div(v-if="progressStep() < 4")
          p Initializing... ({{this.progress}} / 4)
             el-button(circle plain type="primary" :loading="true" size="normal") 
        div(v-else="")
          QuickAccess
    el-row
      el-col(:span="20" :offset="2")
        Highlights
</template>


<script>
import { mapGetters } from 'vuex'
import SearchBar from '../components/search-bar.vue'
import QuickAccess from '../components/quick-access/index.vue'
import Highlights from '../components/highlights/index.vue'

export default {
  name: 'home',
  components: {
    SearchBar,
    QuickAccess,
    Highlights,
  },
  methods: {
    progressStep () {
      return this.progress
    }
  },
  computed: {
    thisYear () {
      return new Date().getFullYear()
    },
    ...mapGetters(['db_stats', 'progress'])
  },
}
</script>

</script>

<style lang="scss">


</style>
