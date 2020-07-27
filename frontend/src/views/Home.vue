<template lang="pug">
  div
    el-row
      el-col(:span="20" :offset="2")
        p <i>Early Evidence Base</i> (EEB) is an <b>experimental platform</b>
          |  that  combines artificial intelligence with human curation
          |  and expert peer-review to highlight results posted in
          |
          a(href="https://biorxiv.org") bioRxiv
          |  preprints.
        p
          |The EEB platform is a technology experiment developed by
          |
          a(href="https://embopress.org") EMBO Press.

        p EEB helps user to browse preprints in several ways
        ul
          li Expert reviews linked to preprints provide in-depth analyses of the reported evidence.
          li Hypotheses related to the biology of SARS-CoV-2/COVID-19 are highlighted and linked to the reespective studies.
          li A selection of recent SARS-CoV-2 preprints are  highlighted based on the variety of experimental approaches used and the number of biological topics investigated.
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
