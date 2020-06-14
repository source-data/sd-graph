<template lang="pug">
  div
    h5 Recent hypotheses tested in preprints related to SARS-CoV-2/COVID-19.
    el-radio-group(@change="onSelect" v-model="selectedHyp" size="mini" fill="#406482")
      span(v-for="hyp in hypList").spaced-row
        el-radio-button(:label="hyp.id" style="margin: 1px;")
          el-tag(v-for="ctrl_var in hyp.hyp.ctrl_v" size="mini" type="danger" effect="dark") {{ ctrl_var }}
          i(class="el-icon-minus")
          i(class="el-icon-question")
          i(class="el-icon-right")
          el-tag(v-for="meas_var in hyp.hyp.meas_v" size="mini" type="" effect="dark") {{ meas_var }} 
      br
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
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
      this.$emit('change', selectedItemId)
    },
  },
}
</script>
