<template lang="pug">
v-container(fluid).pa-0.ma-0
  v-row.pa-3
    v-col(cols=3)
      v-row
        ByReviewingService
    v-col(cols=9)
      v-row
        Highlights
</template>


<script>
import Highlights from '../components/highlights/index.vue'
import ByReviewingService from '../components/quick-access/by-reviewing-service.vue'

import { REFEREED_PREPRINTS, FULLTEXT_SEARCH } from '../components/quick-access/tab-names'
import { serviceSlug2Id } from '../store/by-reviewing-service'

function getStoreNameForCollection (collection) {
  let storeName = undefined
  switch (collection) {
    case 'refereed-preprints':
      storeName = REFEREED_PREPRINTS
      break
    case 'search':
      storeName = FULLTEXT_SEARCH
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
  const storeName = getStoreNameForCollection(collection)
  switch (storeName) {
    case REFEREED_PREPRINTS:
      initialLoad = REFEREED_PREPRINTS
      delayedLoad = []
      break;
    case FULLTEXT_SEARCH:
      initialLoad = null
      delayedLoad = []
      break;
  }

  const initialLightAppLoad = (storeName) => {
    if (!storeName) {
      return Promise.resolve()
    }
    return $store.dispatch(`${storeName}/getAll`)
      .then(() => {
        if (storeName === REFEREED_PREPRINTS) {
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
    Highlights,
    ByReviewingService
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
      this.$store.commit('highlights/updateCurrentPage', 1) // reset pagination if we are navigating to a different sub-app
    }
    const storeName = getStoreNameForCollection(to.params.collection)
    this.$store.dispatch('highlights/listByCurrent', storeName)
    next()
  },

}
</script>

<style lang="scss">


</style>
