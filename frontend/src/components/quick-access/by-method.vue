<template lang="pug">
  el-radio-group(@change="onSelect" v-model="selectedMethod")
    div(v-for="method in methodList")
      el-radio(:label="method.id")
        | {{ method.item_name }}
      br
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
      byMethod: [],
      selectedMethod: undefined,
    }
  },
  computed: {
    ...mapGetters('byMethod', [
      'records',
    ]),
    methodList () {
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