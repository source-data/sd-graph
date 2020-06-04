<template lang="pug">
  el-radio-group(@change="onSelect" v-model="selectedMol")
    el-row(v-for="mol in molList").spaced-row
      el-radio(:label="mol.id")
        | {{ mol.id }}
      br
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
      selectedMol: undefined,
    }
  },
  computed: {
    ...mapGetters('byMol', [
      'records',
    ]),
    molList () {
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
