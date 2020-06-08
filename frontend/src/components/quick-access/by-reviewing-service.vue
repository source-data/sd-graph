<template lang="pug">
  el-radio-group(@change="onSelect" v-model="selectedRev")
    el-radio-button(v-for="rev in reviweingList" :label="rev.id")
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
    reviweingList () {
      return this.records
    },
  },
  methods: {
    onSelect (selectedItemId) {
      this.$emit('change', selectedItemId)
    },
  },
}
</script>
