<template lang="pug">
  div
    el-row(type="flex" class="row-bg" justify="space-between")
      el-col
        p.margin-5
          small Select a reviewing service
        el-radio-group(size="mini" @change="onSelect" v-model="selectedRev")
          el-radio-button(v-for="id in reviewingList" :label="id") {{ displayJournal(id) }}
      el-col
        p.margin-5
          small Sort by:
        el-radio-group(v-model="sortBy" size="mini" @change="sortRecords")
          el-radio-button(label="pub_date")
            | preprint date
          el-radio-button(label="posting_date")
            | reviewing date
        el-switch(
          style="margin-left:10px"
          v-model="sortDirection"
          @change="sortRecords"
          active-icon-class="el-icon-sort-up"
          active-value="asc"
          active-color="#409EFF"
          inactive-icon-class="el-icon-sort-down"
          inactive-value="desc"
          inactive-color="#409EFF"
        )
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
      selectedRev: 'review commons',
      sortBy: 'posting_date',
      sortDirection: 'desc',
    }
  },
  computed: {
    ...mapGetters('byReviewingService', [
      'records',
    ]),
    ...mapGetters(['journalName']),
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
    displayJournal(id) {
      return this.journalName(id)
    }
  },
}
</script>
