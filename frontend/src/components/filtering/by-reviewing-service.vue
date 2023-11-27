<template lang="pug">
v-card(flat)
  v-card-title Review sources
  v-card-text
    v-chip-group(v-model="selectedRev" mandatory column)
      span(v-for="serviceId in this.reviewingList" :key="`${serviceId}-chip`")
        router-link(:to="{ path: `/refereed-preprints/${serviceId2Slug(serviceId)}` }")
          v-chip(
            :value="serviceId2Slug(serviceId)" :disabled="loadingRecords"
          )
            img(v-if="imageFileName(serviceId2Slug(serviceId))" :src="require(`@/assets/chips/` + imageFileName(serviceId2Slug(serviceId)))" height="24px" :alt="serviceId2Name(serviceId)").pa-1
            | {{ serviceId2Name(serviceId) }}

    InfoCardsReviewServiceSummaryGraph(
      :service_name="serviceId2Name(serviceSlug2Id(selectedRev))",
      :url="reviewingService(serviceSlug2Id(selectedRev)).url",
      :peer_review_policy="reviewingService(serviceSlug2Id(selectedRev)).peer_review_policy",
      :review_requested_by="reviewingService(serviceSlug2Id(selectedRev)).review_requested_by",
      :reviewer_selected_by="reviewingService(serviceSlug2Id(selectedRev)).reviewer_selected_by",
      :review_coverage="reviewingService(serviceSlug2Id(selectedRev)).review_coverage",
      :reviewer_identity_known_to="reviewingService(serviceSlug2Id(selectedRev)).reviewer_identity_known_to",
      :competing_interests="reviewingService(serviceSlug2Id(selectedRev)).competing_interests",
      :public_interaction="reviewingService(serviceSlug2Id(selectedRev)).public_interaction",
      :opportunity_for_author_response="reviewingService(serviceSlug2Id(selectedRev)).opportunity_for_author_response",
      :recommendation="reviewingService(serviceSlug2Id(selectedRev)).recommendation",
    ).px-0.mt-2
</template>

<script>

import { mapGetters, mapState } from 'vuex'
import { serviceId2Slug, serviceId2Name, serviceSlug2Id } from '../../store/by-reviewing-service'
import InfoCardsReviewServiceSummaryGraph from '../review-service-info/review-service-summary-graph.vue'

export default {
  components: {
    InfoCardsReviewServiceSummaryGraph,
  },
  data () {
    return {
      selectedRev: undefined,
    }
  },
  beforeMount () {
    this.selectedRev = this.$route.params.service
  },
  computed: {
    ...mapState('highlights', ['loadingRecords']),
    ...mapGetters('byReviewingService', ['records', 'reviewingService']),
    reviewingList () {
      const ids =  this.records.map(
        (r) => {return r.id}
      ).sort().reverse()
      return ids
    },
  },
  methods: {
    // Returns the filename for the  image that should be associated with the chip's text, or null if none is found
    imageFileName(slug) {
      const availableSourceLogos = require.context('../../assets/chips/', true, /\.(svg|png|jpg)/).keys()
      let filename = availableSourceLogos.find(i => i.includes(slug))
      if (filename)
        return filename.substring(2) // substring to remove the `./` part of the name
      else return null
    },
    serviceId2Slug,
    serviceId2Name,
    serviceSlug2Id
  },
}
</script>

<style lang="scss" scoped>
/* After the user clicks on a reviewing service's button, all rev service buttons are disabled.
 * This makes the clicked-on-but-disabled button distinct from all the other disabled buttons.
 */
.v-btn--active.v-btn--disabled::before {
  opacity: 0.5 !important;
}
</style>