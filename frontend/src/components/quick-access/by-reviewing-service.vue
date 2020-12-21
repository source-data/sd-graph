<template lang="pug">
  v-card(class="pa-5" outlined)
    v-card-title Preprints linked to peer reviews
    v-card-text
      v-btn-toggle(v-model="selectedRev" mandatory)
        v-container.pa-0
          v-row(v-for="i in 2" :key="`row-${i}`" justify="space-between")
            v-col(v-for="j in 3" :key="`col-${j}`")
              router-link(:to="{ path: `/refereed-preprints/${serviceId2Slug(reviewingListId(i, j))}` }")
                v-btn(:value="serviceId2Slug(reviewingListId(i, j))" :disabled="loadingRecords") {{ serviceId2Name(reviewingListId(i, j)) }}
      div(v-html="selectedReviewingServiceDescription").pt-3

</template>

<script>
import { mapGetters, mapState } from 'vuex'
import { serviceId2Slug, serviceId2Name, getReviewingServiceDescription } from '../../store/by-reviewing-service'

export default {
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
    selectedReviewingServiceDescription () {
      return getReviewingServiceDescription(this.selectedRev)
    }
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