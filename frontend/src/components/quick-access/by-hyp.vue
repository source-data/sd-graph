<template lang="pug">
  el-radio-group(@change="onSelect" v-model="selectedHyp")
    div(v-for="hyp in hypList")
      el-radio(:label="hyp.id")
        | ({{ hyp.hyp.ctrl_v }}) -?→ ({{ hyp.hyp.meas_v }})
      br
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
      byHyp: [],
      selectedHyp: undefined,
    }
  },
  computed: {
    ...mapGetters('byHyp', [
      'records',
    ]),
    hypList () {
      return this.records
    },
  },
  methods: {
    onSelect (selectedItemId) {
      console.debug('onSelect',selectedItemId)
      this.$emit('change', selectedItemId)
    },
  },
}
</script>