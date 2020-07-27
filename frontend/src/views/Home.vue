<template lang="pug">
  div
    el-row
      el-col(:span="20" :offset="2")
        el-card.box-card
          p <i>Early Evidence Base</i> (EEB) is an <b>experimental platform</b>
            |  that  combines artificial intelligence with human curation
            |  and expert peer-review to highlight results posted in
            |
            a(href="https://biorxiv.org" target="_blank") bioRxiv
            |  preprints.
          p
            |The EEB platform is a technology experiment developed by
            |
            a(href="https://embopress.org" target="_blank") EMBO Press 
            | and 
            a(href="https://sourcedata.io" target="_blank") SourceData
            |. 
          p Follow 
            a(href="https://twitter.com/EarlyEvidence" target="_blank") @EarlyEvidence
            |  on Twitter to receive updates and new highlighted preprints.
          p Discover preprints with one of these methods:
          ul
            li
              //- i(class="el-icon-reading")
              b  Refereed Preprints: 
              |  browse preprints that are linked to expert reviews.
            li
              //- i(class="fas el-icon-fa-flask")
              b  COVID-19 hypotheses: 
              |  find recent studies related to the biology of SARS-CoV-2/COVID-19 based on the hypotheses they are testing.
            li
              //- i(class="el-icon-magic-stick")
              b  Automagic:
              |  check out a selection of 20 SARS-CoV-2 preprints automatically highlighted based on the diversity of experimental approaches used and biological topics investigated.
            li
              //- i(class="el-icon-search")
              b  Search COVID-19 preprints:
              |  find preprints by keyword, author name or doi.


    el-row
      el-col(:span="20" :offset="2")
        div(v-if="progressStep() < 4")
          p Initializing... ({{this.progress}} / 4)
             el-button(circle plain type="primary" :loading="true" size="normal")
        div(v-else="")
          br
          el-card.box-card
            QuickAccess
    el-row
      el-col(:span="20" :offset="2")
        Highlights
</template>


<script>
import { mapGetters } from 'vuex'
import QuickAccess from '../components/quick-access/index.vue'
import Highlights from '../components/highlights/index.vue'

export default {
  name: 'home',
  components: {
    QuickAccess,
    Highlights,
  },
  methods: {
    progressStep () {
      return this.progress
    }
  },
  computed: {
    ...mapGetters(['db_stats', 'progress'])
  },
}
</script>

</script>

<style lang="scss">


</style>
