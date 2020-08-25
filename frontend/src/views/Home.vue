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

function getStoreNameForCollection (collection, service) {
  let storeName = undefined
  switch (collection) {
    case 'refereed_preprints':
      storeName = REFEREED_PREPRINTS_TAB
      break
    case 'covid19':
      switch (service) {
        case 'by_hyp':
          storeName = COVID19_HYP_TAB
          break
        case 'automagic':
          storeName = COVID19_AUTOMAGIC_TAB
          break
        case 'search':
          storeName = COVID19_SEARCH
          break
      }
      break
  }
  return storeName
}

function initApp (collection, service, $store) {
  /**
   * App initialization
   * This function is responsible of loading required data in multiple steps
   * prioritising the content that needs to be rendered first, based on the
   * QuickAccess tab that is currently selected
   */
  let initialLoad = null
  let delayedLoad = []
  const storeName = getStoreNameForCollection(collection, service)
  switch (storeName) {
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
        if (storeName === REFEREED_PREPRINTS_TAB) {
          const serviceId = serviceSlug2Id(service)
          $store.commit('byReviewingService/showRecord', { id: serviceId })
        }
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
  props: {
    collection: String,
    service: String,
  },
  computed: {
    activeTab () {
      return getStoreNameForCollection(this.collection, this.service)
    }
  },

  created () {
    initApp(this.collection, this.service, this.$store)
  },

  beforeRouteUpdate (to, from, next) {
    if (to.params.collection === 'refereed_preprints' && to.params.service !== from.params.service) {
      const serviceId = serviceSlug2Id(to.params.service)
      this.$store.commit('byReviewingService/showRecord', { id: serviceId })
    }
    const storeName = getStoreNameForCollection(to.params.collection, to.params.service)
    this.$store.dispatch('highlights/listByCurrent', storeName)
    next()
  },

}
</script>

<style lang="scss">


</style>
