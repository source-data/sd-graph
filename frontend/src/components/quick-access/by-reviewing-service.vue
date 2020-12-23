<template lang="pug">
  v-card(outlined).pa-5
    v-card-title Preprints linked to peer reviews
    v-card-text
      v-container
        v-row()
          v-col(cols=7)
            v-btn-toggle(v-model="selectedRev" mandatory)
              v-container.pa-0
                v-row(v-for="i in 2" :key="`row-${i}`" justify="space-between")
                  v-col(v-for="j in 3" :key="`col-${j}`")
                    router-link(:to="{ path: `/refereed-preprints/${serviceId2Slug(reviewingListId(i, j))}` }")
                      v-badge(
                          content="123"
                          overlap
                        )
                        v-btn(:value="serviceId2Slug(reviewingListId(i, j))" :disabled="loadingRecords")
                          | {{ serviceId2Name(reviewingListId(i, j)) }}
          v-col(cols=5)
            //- p {{ selectedReviewingServiceDescription(selectedRev) }}
            InfoCardsReviewServiceSummary(
              service_name="Review Commons",
              url="sdfksdl",
              evaluation_type='peer_review',
              certification=true,
              auhor_driven=false,
              journal_independent=true,
            )

</template>

<script>

import { mapGetters, mapState } from 'vuex'
import { serviceId2Slug, serviceId2Name, getReviewingServiceDescription, } from '../../store/by-reviewing-service'
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
  mounted () {
    this.selectedRev = this.$route.params.service
  },
  computed: {
    ...mapState('highlights', ['loadingRecords']),
    ...mapGetters('byReviewingService', ['records']),
    reviewingList () {
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
      return this.reviewingList[(i-1)*3 + (j-1)]
    },
    serviceId2Slug,
    serviceId2Name,
    selectedReviewingServiceDescription (serviceSlug) {
      console.debug("spread", getReviewingServiceDescription(serviceSlug))
      return getReviewingServiceDescription(serviceSlug)
    }
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