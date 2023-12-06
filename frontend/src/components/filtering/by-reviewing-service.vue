<template lang="pug">
v-card(flat)
  v-card-title Review sources
  v-card-text
    v-chip-group(v-model="selectedReviewer" mandatory column)
      span(v-for="service in this.reviewing_services" :key="`${service.id}-chip`")
        v-chip(:value="service.id" :disabled="loadingRecords" filter filter-icon="mdi-check" 
               active-class="active-chip" text-color="black")
          img(v-if="imageFileName(serviceId2Slug(service.id))" :src="require(`@/assets/chips/` + imageFileName(serviceId2Slug(service.id)))" height="24px" :alt="serviceId2Name(service.id)").pa-1
          | {{ serviceId2Name(service.id) }}

    InfoCardsReviewServiceSummaryGraph(
      :service_name="serviceId2Name(selectedReviewer)",
      :url="reviewingService(selectedReviewer).url",
      :peer_review_policy="reviewingService(selectedReviewer).peer_review_policy",
      :review_requested_by="reviewingService(selectedReviewer).review_requested_by",
      :reviewer_selected_by="reviewingService(selectedReviewer).reviewer_selected_by",
      :review_coverage="reviewingService(selectedReviewer).review_coverage",
      :reviewer_identity_known_to="reviewingService(selectedReviewer).reviewer_identity_known_to",
      :competing_interests="reviewingService(selectedReviewer).competing_interests",
      :public_interaction="reviewingService(selectedReviewer).public_interaction",
      :opportunity_for_author_response="reviewingService(selectedReviewer).opportunity_for_author_response",
      :recommendation="reviewingService(selectedReviewer).recommendation",
    ).px-0.mt-2
</template>

<script>

import { mapState, mapGetters } from 'vuex'
import { serviceId2Slug, serviceId2Name } from '../../store/by-filters'
import InfoCardsReviewServiceSummaryGraph from '../review-service-info/review-service-summary-graph.vue'

export default {
  components: {
    InfoCardsReviewServiceSummaryGraph,
  },
  data () {
    return {}
  },
  computed: {
    ...mapState('byFilters', ['reviewing_services', 'loadingRecords', 'reviewed_by']),
    ...mapGetters('byFilters', ['reviewingService']),

    selectedReviewer: {
      set(value) {
        this.$store.commit("byFilters/setReviewedBy", value);
        this.$store.commit("byFilters/setCurrentPage", 1);
        this.$store.dispatch('byFilters/updateRecords');
      },
      get() {
        return this.reviewed_by
      }
    }
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
    serviceId2Name
  },
}
</script>

<style lang="scss" scoped>
.active-chip {
  background-color: var(--v-accent-lighten1);
}
</style>