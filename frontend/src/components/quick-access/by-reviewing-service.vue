<template lang="pug">
  el-radio-group(@change="onSelect" v-model="selectedRev")
    el-radio-button(v-for="rev in reviewingList" :label="journalName(rev.id)")
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
    reviewingList () {
      return this.records
    },
  },
  methods: {
    onSelect (selectedItemId) {
      // need to transform the label value into a key
      this.$emit('change', selectedItemId.toLowerCase())
    },
    journalName (id) {
      return this.$store.getters.journalName[id]
    }
  },
}
</script>
