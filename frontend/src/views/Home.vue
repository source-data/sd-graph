<template lang="pug">
  div
    el-row
      el-col(:span="20" :offset="2")
        el-card.box-card
          p <i>Early Evidence Base</i> (EEB) is an <b>experimental platform</b>
            |  that  combines artificial intelligence with human curation
            |  and expert peer-review to highlight results posted in
            |
            a(href="https://biorxiv.org" target="_blank" rel="noopener") bioRxiv
            |  preprints. EEB is a technology experiment developed by
            |
            a(href="https://embopress.org" target="_blank" rel="noopener") EMBO Press
            |
            | and
            |
            a(href="https://sourcedata.io" target="_blank" rel="noopener") SourceData
            |.
          p
            | Follow
            |
            a(href="https://twitter.com/EarlyEvidence" target="_blank" rel="noopener") @EarlyEvidence
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
              |  find recent studies related to the biology of SARS-CoV-2/COVID-19 based on hypotheses they are testing.
            li
              //- i(class="el-icon-magic-stick")
              b  Automagic:
              |  check out a selection of 20 SARS-CoV-2 preprints automatically highlighted based on their diversity in experimental approaches and biological topics.
            li
              //- i(class="el-icon-search")
              b  Search COVID-19 preprints:
              |  find preprints by keyword, author name or doi.


    el-row
      el-col(:span="20" :offset="2")
        br
        el-card.box-card
          QuickAccess(:activeTab="activeTab")
    el-row
      el-col(:span="20" :offset="2")
        Highlights
</template>


<script>
import QuickAccess from '../components/quick-access/index.vue'
import Highlights from '../components/highlights/index.vue'
import { REFEREED_PREPRINTS_TAB, COVID19_HYP_TAB, COVID19_AUTOMAGIC_TAB, COVID19_SEARCH } from '../components/quick-access/tab-names'

function chooseActiveTabBasedOnCurrentRoute (to) {
  switch (to.name) {
    case 'RefereedPreprints':
      return REFEREED_PREPRINTS_TAB
    case 'Covid19ByHyp':
      return COVID19_HYP_TAB
    case 'Covid19Automagic':
      return COVID19_AUTOMAGIC_TAB
    case 'Covid19Search':
      return COVID19_SEARCH
    default:
      return REFEREED_PREPRINTS_TAB
  }
}

function initApp (activeTab, $store) {
  /**
   * App initialization
   * This function is responsible of loading required data in multiple steps
   * prioritising the content that needs to be rendered first, based on the
   * QuickAccess tab that is currently selected
   */
  let initialLoad = null
  let delayedLoad = []
  switch (activeTab) {
    case REFEREED_PREPRINTS_TAB:
      initialLoad = REFEREED_PREPRINTS_TAB
      delayedLoad = [
        COVID19_HYP_TAB,
        COVID19_AUTOMAGIC_TAB,
      ]
      break;
    case COVID19_HYP_TAB:
      initialLoad = COVID19_HYP_TAB
      delayedLoad = [
        REFEREED_PREPRINTS_TAB,
        COVID19_AUTOMAGIC_TAB,
      ]
      break;
    case COVID19_AUTOMAGIC_TAB:
      initialLoad = COVID19_AUTOMAGIC_TAB
      delayedLoad = [
        REFEREED_PREPRINTS_TAB,
        COVID19_HYP_TAB,
      ]
      break;
    case COVID19_SEARCH:
      initialLoad = null
      delayedLoad = [
        COVID19_HYP_TAB,
        REFEREED_PREPRINTS_TAB,
        COVID19_AUTOMAGIC_TAB,
      ]
      break;
  }

  const initialLightAppLoad = (storeName) => {
    if (!storeName) {
      return Promise.resolve()
    }
    return $store.dispatch(`${storeName}/getAll`)
      .then(() => {
        return $store.dispatch('highlights/listByCurrent', storeName)
      })
      .then(() => {
        $store.commit('highlights/sortRecords', {
            sortBy: 'posting_date',
            direction: 'desc',
          })
        $store.commit('highlights/updateSelectedTab', storeName)
      })
  }
  const secondHeavyFullAppLoad = (delayedStores) => {
    $store.dispatch('statsFromFlask')
    delayedStores.forEach((storeName) => {
      $store.dispatch(`${storeName}/getAll`)
    })
  }
  initialLightAppLoad(initialLoad).then(() => secondHeavyFullAppLoad(delayedLoad))
}

export default {
  name: 'home',
  components: {
    QuickAccess,
    Highlights,
  },
  data () {
    return {
      activeTab: undefined,
    }
  },
  beforeCreate () {
    const activeTab = chooseActiveTabBasedOnCurrentRoute(this.$route)
    initApp(activeTab, this.$store)
  },
  beforeRouteEnter (to, from, next) {
    next((vm) => {
      vm.activeTab = chooseActiveTabBasedOnCurrentRoute(to)
      vm.$store.dispatch('highlights/listByCurrent', vm.activeTab)
    })
  },
  beforeRouteUpdate (to, from, next) {
    this.activeTab = chooseActiveTabBasedOnCurrentRoute(to)
    next()
  },
}
</script>

<style lang="scss">


</style>
