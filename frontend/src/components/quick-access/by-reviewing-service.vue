<template lang="pug">
  v-container
      v-row(align="center")
        v-col(cols=8)
          v-card(outlined).pa-5
            v-card-title Preprints linked to formal reviews
            v-card-text
              v-btn-toggle(v-model="selectedRev" mandatory)
                v-container.pa-0
                  v-row(v-for="i in 3" :key="`row-${i}`")
                    v-col(cols=6 v-for="j in 2" :key="`col-${j}`")
                      div(v-if="reviewingListId(i, j)")
                        router-link(:to="{ path: `/refereed-preprints/${serviceId2Slug(reviewingListId(i, j))}` }")
                          span().v-badge.v-badge--dot.v-badge--bordered
                            //- v-badge(dot overlap)
                            v-btn(
                              :value="serviceId2Slug(reviewingListId(i, j))" :disabled="loadingRecords"
                            )
                              | {{ serviceId2Name(reviewingListId(i, j)) }}
                            span.v-badge__wrapper
                              span(
                                v-if="reviewingService(reviewingListId(i, j)).post_review_decision"
                                style="inset: auto auto calc(100% - 5px) calc(100% - 28px);").v-badge__badge.lime.darken-5
                              span(
                                v-if="reviewingService(reviewingListId(i, j)).author_driven_submissions"
                                style="inset: auto auto calc(100% - 5px) calc(100% - 18px);").v-badge__badge.amber.darken-2
                              span(
                                v-if="reviewingService(reviewingListId(i, j)).pre_review_triage"
                                style="inset: auto auto calc(100% - 5px) calc(100% - 8px);").v-badge__badge.purple
        v-col(v-if="selectedRev" cols=4)
          InfoCardsReviewServiceSummary(
            :service_name="serviceId2Name(serviceSlug2Id(selectedRev))",
            :url="reviewingService(serviceSlug2Id(selectedRev)).url",
            :certification="reviewingService(serviceSlug2Id(selectedRev)).post_review_decision", 
            :author_driven="reviewingService(serviceSlug2Id(selectedRev)).author_driven_submissions",
            :pre_review_triage="reviewingService(serviceSlug2Id(selectedRev)).pre_review_triage",
          )

</template>

<script>

import { mapGetters, mapState } from 'vuex'
import { serviceId2Slug, serviceId2Name, serviceSlug2Id } from '../../store/by-reviewing-service'
import InfoCardsReviewServiceSummary from './info-cards/review-service-summary.vue'


export default {
  components: {
    InfoCardsReviewServiceSummary,
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
      console.debug("reviewingService('elife')", this.reviewingService('elife'))
      const ids =  this.records.map(
        (r) => {return r.id}
      ).sort().reverse()
      return ids
    },
  },
  methods: {
    onSelect (selectedItemId) {
      this.$emit('change', selectedItemId)
    },
    reviewingListId(i, j) {
      return this.reviewingList[(i-1)*2 + (j-1)]
    },
    serviceId2Slug,
    serviceId2Name,
    serviceSlug2Id
  },
}
</script>

<style lang="scss" scoped>
  .router-link-active {
    color: #FFFFFF;
    background-color: #409EFF;
    border-color: #409EFF;

    &:hover {
      color: #EEE;
    }
  }
</style>