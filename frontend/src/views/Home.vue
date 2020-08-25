<template lang="pug">
  div
    el-row
      el-col(:span="20" :offset="2")
        Intro
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
import Intro from '../layouts/intro.vue'

import { REFEREED_PREPRINTS_TAB, COVID19_HYP_TAB, COVID19_AUTOMAGIC_TAB, COVID19_SEARCH } from '../components/quick-access/tab-names'
import { serviceSlug2Id } from '../store/by-reviewing-service'

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
    Intro,
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
      vm.chooseActiveReviewingServiceBasedOnCurrentRoute(to, from)
      vm.activeTab = chooseActiveTabBasedOnCurrentRoute(to)
      vm.$store.dispatch('highlights/listByCurrent', vm.activeTab)
    })
  },
  beforeRouteUpdate (to, from, next) {
    this.chooseActiveReviewingServiceBasedOnCurrentRoute(to, from)
    this.activeTab = chooseActiveTabBasedOnCurrentRoute(to)
    next()
  },
  methods: {
    chooseActiveReviewingServiceBasedOnCurrentRoute (to, from) {
      if (to.name === 'RefereedPreprints' && to.params.service !== from.params.service) {
        const serviceId = serviceSlug2Id(to.params.service)
        this.$store.commit('byReviewingService/showRecord', { id: serviceId })
        this.$store.dispatch('highlights/listByCurrent', 'byReviewingService')
      }
    }
  },
}
</script>

<style lang="scss">


</style>
