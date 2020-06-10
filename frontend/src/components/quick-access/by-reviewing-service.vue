<template lang="pug">
  el-radio-group(@change="onSelect" v-model="selectedRev")
    el-radio-button(v-for="rev in reviewingList" :label="displayJournal(rev.id)")
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
      selectedRev: undefined,
    }
  },
  computed: {
    ...mapGetters('byReviewingService', [
      'records',
    ]),
    ...mapGetters(['journalName']),
    reviewingList () {
      return this.records
    },
  },
  methods: {
    onSelect (selectedItemId) {
      // need to transform the label value into a key
      this.$emit('change', selectedItemId.toLowerCase())
    },
    displayJournal(id) {
      return this.journalName(id)
    }
  },
}
</script>
