<template lang="pug">
  v-container
      v-row(align="center")
        v-col(cols=7)
          v-card(outlined).pa-5
            v-card-title Preprints linked to formal reviews
            v-card-text
              v-btn-toggle(v-model="selectedRev" mandatory)
                v-container.pa-0
                  v-row(v-for="i in 3" :key="`row-${i}`")
                    v-col(cols="6" v-for="j in 2" :key="`col-${j}`")
                      router-link(:to="{ path: `/refereed-preprints/${serviceId2Slug(reviewingListId(i, j))}` }")
                        span().v-badge.v-badge--dot.v-badge--bordered
                          //- v-badge(dot overlap)
                          v-btn(
                            :value="serviceId2Slug(reviewingListId(i, j))" :disabled="loadingRecords"
                          )
                            | {{ serviceId2Name(reviewingListId(i, j)) }}
                          span.v-badge__wrapper
                            span(
                              v-if="serviceSlug2Props(serviceId2Slug(reviewingListId(i, j))).journal_independent"
                              style="inset: auto auto calc(100% - 5px) calc(100% - 28px);").v-badge__badge.lime.darken-5
                            span(
                              v-if="serviceSlug2Props(serviceId2Slug(reviewingListId(i, j))).certification"
                              style="inset: auto auto calc(100% - 5px) calc(100% - 18px);").v-badge__badge.amber.darken-2
                            span(
                              v-if="serviceSlug2Props(serviceId2Slug(reviewingListId(i, j))).author_driven"
                              style="inset: auto auto calc(100% - 5px) calc(100% - 8px);").v-badge__badge.purple
        v-col(v-if="selectedRev")
          InfoCardsReviewServiceSummary(
            :service_name="serviceSlug2Props(selectedRev).service_name",
            :url="serviceSlug2Props(selectedRev).url",
            :evaluation_type="serviceSlug2Props(selectedRev).evaluation_type",
            :certification="serviceSlug2Props(selectedRev).certification", 
            :author_driven="serviceSlug2Props(selectedRev).author_driven",
            :journal_independent="serviceSlug2Props(selectedRev).journal_independent",
          )

</template>

<script>

import { mapGetters, mapState } from 'vuex'
import { serviceId2Slug, serviceId2Name, serviceSlug2Props } from '../../store/by-reviewing-service'
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
      return this.reviewingList[(i-1)*2 + (j-1)]
    },
    serviceId2Slug,
    serviceId2Name,
    serviceSlug2Props,
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