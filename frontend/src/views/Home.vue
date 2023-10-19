<template lang="pug">
  v-container(fluid)
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

import { REFEREED_PREPRINTS, AUTO_TOPICS, AUTOMAGIC, FULLTEXT_SEARCH } from '../components/quick-access/tab-names'
import { serviceSlug2Id } from '../store/by-reviewing-service'

function getStoreNameForCollection (collection, service) {
  let storeName = undefined
  switch (collection) {
    case 'refereed-preprints':
      storeName = REFEREED_PREPRINTS
      break
    case 'all':
      switch (service) {
        case 'auto-topics':
          storeName = AUTO_TOPICS
          break
        case 'automagic':
          storeName = AUTOMAGIC
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
    case REFEREED_PREPRINTS:
      initialLoad = REFEREED_PREPRINTS
      delayedLoad = [
        AUTO_TOPICS,
        AUTOMAGIC,
      ]
      break;
    case AUTO_TOPICS:
      initialLoad = AUTO_TOPICS
      delayedLoad = [
        REFEREED_PREPRINTS,
        AUTOMAGIC,
      ]
      break;
    case AUTOMAGIC:
      initialLoad = AUTOMAGIC
      delayedLoad = [
        REFEREED_PREPRINTS,
        AUTO_TOPICS,
      ]
      break;
    case FULLTEXT_SEARCH:
      initialLoad = null
      delayedLoad = [
        AUTO_TOPICS,
        REFEREED_PREPRINTS,
        AUTOMAGIC,
      ]
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
      this.$store.commit('highlights/updateCurrentPage', 1) // reset pagination if we are navigating to a different sub-app
    }
    const storeName = getStoreNameForCollection(to.params.collection, to.params.service)
    this.$store.dispatch('highlights/listByCurrent', storeName)
    next()
  },

}
</script>

<style lang="scss">


</style>
