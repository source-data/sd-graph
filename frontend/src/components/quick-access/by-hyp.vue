<template lang="pug">
  v-card(class="pa-5" outlined)
    v-card-title Recent hypotheses tested in preprints related to SARS-CoV-2/COVID-19.
    v-btn-toggle(v-for="hyp in hypList" @change="onSelect" v-model="selectedHyp")
       v-btn(:value="hyp.id" small text class="ma-1")
          v-chip(v-for="ctrl_var in hyp.hyp.ctrl_v" color="red lighten-3" x-small) {{ ctrl_var }}
          v-icon(small) mdi-minus
          v-icon(small) mdi-help-circle-outline
          v-icon(small) mdi-arrow-right
          v-chip(v-for="meas_var in hyp.hyp.meas_v" color="blue lighten-3" x-small) {{ meas_var }} 
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
      // default value
      selectedHyp: 0
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

