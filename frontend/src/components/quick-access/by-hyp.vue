<template lang="pug">
  el-radio-group(@change="onSelect" v-model="selectedHyp")
    el-row(v-for="hyp in hypList").spaced-row
        el-radio(:label="hyp.id")
          el-tag(size="mini" type="danger" effect="dark") {{ hyp.hyp.ctrl_v }}
          i(class="el-icon-minus")
          i(class="el-icon-question")
          i(class="el-icon-right")
          el-tag(size="mini" type="" effect="dark") {{ hyp.hyp.meas_v }} 
    br
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
      //byHyp: [],
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
