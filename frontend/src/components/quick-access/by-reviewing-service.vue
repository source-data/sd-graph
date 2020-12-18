<template lang="pug">
  v-card(class="pa-5" outlined)
    v-card-title Preprints linked to peer reviews
    v-card-text
      v-row
        v-col
          p Reviewing services:
          v-btn-toggle(v-model="selectedRev" mandatory)
            router-link(v-for="id in reviewingList" :key="serviceId2Slug(id)" :to="{ path: `/refereed-preprints/${serviceId2Slug(id)}` }")
              v-btn(small :value="serviceId2Slug(id)") {{ serviceId2Name(id) }}
          div(v-html="selectedReviewingServiceDescription").pt-3

</template>

<script>
import { mapGetters } from 'vuex'
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