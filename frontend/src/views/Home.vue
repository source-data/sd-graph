<template lang="pug">
  v-container()
    v-row
      v-col
        Intro
    v-row
      v-col
        QuickAccess
    v-row
      v-col
        Highlights
</template>


<script>
import QuickAccess from '../components/quick-access/index.vue'
import Highlights from '../components/highlights/index.vue'
import Intro from '../layouts/intro.vue'

import { REFEREED_PREPRINTS_TAB, BY_AUTO_TOPICS, COVID19_AUTOMAGIC_TAB, FULLTEXT_SEARCH } from '../components/quick-access/tab-names'
import { serviceSlug2Id } from '../store/by-reviewing-service'

function getStoreNameForCollection (collection, service) {
  let storeName = undefined
  switch (collection) {
    case 'refereed-preprints':
      storeName = REFEREED_PREPRINTS_TAB
      break
    case 'covid19':  // this will eventuall disapper, automagic will be service from collection /all or from new set of collections
      switch (service) {
        case 'automagic':
          storeName = COVID19_AUTOMAGIC_TAB
          break
      }
      break
    case 'all':
      switch (service) {
        case 'by-auto-topics':
          storeName = BY_AUTO_TOPICS
          break
        case 'search':
          storeName = FULLTEXT_SEARCH
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
        BY_AUTO_TOPICS,
        COVID19_AUTOMAGIC_TAB,
      ]
      break;
    case BY_AUTO_TOPICS:
      initialLoad = BY_AUTO_TOPICS
      delayedLoad = [
        REFEREED_PREPRINTS_TAB,
        COVID19_AUTOMAGIC_TAB,
      ]
      break;
    case COVID19_AUTOMAGIC_TAB:
      initialLoad = COVID19_AUTOMAGIC_TAB
      delayedLoad = [
        REFEREED_PREPRINTS_TAB,
        BY_AUTO_TOPICS,
      ]
      break;
    case FULLTEXT_SEARCH:
      initialLoad = null
      delayedLoad = [
        BY_AUTO_TOPICS,
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

  created () {
    initApp(this.collection, this.service, this.$store)
  },

  beforeRouteUpdate (to, from, next) {
    if (to.params.collection === 'refereed-preprints' && to.params.service !== from.params.service) {
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
