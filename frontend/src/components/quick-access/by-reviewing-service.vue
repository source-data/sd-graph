<template lang="pug">
  div
    h5 Select refereed preprints by reviewing service and access the associated reviews.
    el-radio-group(@change="onSelect" v-model="selectedRev")
      el-radio-button(v-for="id in reviewingList" :label="id") {{ displayJournal(id) }}
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
      selectedRev: 'review commons',
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
    onSelect (selectedItemId) {
      this.$emit('change', selectedItemId)
    },
    displayJournal(id) {
      return this.journalName(id)
    }
  },
}
</script>
