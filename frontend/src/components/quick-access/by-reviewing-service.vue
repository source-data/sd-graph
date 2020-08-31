<template lang="pug">
  v-card(class="pa-5" outlined)
    v-row
      v-col
        p Select reviewing service:
        v-btn-toggle(m-model="selectedRev" mandatory)
          router-link(v-for="id in reviewingList" :to="{ path: `/refereed_preprints/${serviceId2Slug(id)}` }")
            v-btn(small) {{ serviceId2Name(id) }}
      v-col
        p Sort by:
        v-btn-toggle(v-model="sortBy" @change="sortRecords")
          v-btn(x-small outlined value="pub_date")
            | preprint date
          v-btn(x-small outlined value="posting_date")
            | reviewing date
      v-col
        p Order:
        v-btn-toggle(v-model="sortDirection" @change="sortRecords" mandatory)
          v-btn(x-small icon value="desc")
            v-icon(dense) mdi-sort-descending
          v-btn(x-small icon value="asc")
            v-icon(dense) mdi-sort-ascending
</template>

<script>
import { mapGetters } from 'vuex'
import { serviceId2Slug, serviceId2Name } from '../../store/by-reviewing-service'

export default {
  data () {
    return {
      selectedRev: 'review commons',
      sortBy: 'posting_date',
      sortDirection: 'desc',
    }
  },
  computed: {
    ...mapGetters('byReviewingService', ['records']),
    reviewingList () {
      return this.records.map(
        (r) => {return r.id}
      ).sort().reverse()
    },
  },
  methods: {
    sortRecords() {
      this.$store.commit('highlights/setSortBy', {value: this.sortBy})
      this.$store.commit('highlights/setSortDirection', {value: this.sortDirection})
      this.$store.commit('highlights/sortRecords')
    },
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