<template lang="pug">
  el-radio-group(@change="onSelect" v-model="selectedMethod" size="mini")
      //el-row(v-for="method in methodList").spaced-row
      el-radio-button(v-for="method in methodList" :label="method.id")
        | {{ method.name }}
      br
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
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
