<template lang="pug">
  el-form(:inline="true" :model="search")
    el-form-item(label="search preprints: ")
      el-input(v-model="search.input"
        placeholder="enter search terms"
      )
    el-form-item
      el-button(type="primary" @click="onSubmit") Search
      el-button(@click="cancel") Cancel
</template>

<script>

export default {
  data: function() {
    return {
      search: {
        input: '',
        somethignelse: ''
      } 
    }
  },
  methods: {
    onSubmit()  {
      console.debug('search', this.search.input),
      this.$store.dispatch('fulltextSearch/search', this.search.input).then(
        () => {
          this.$store.dispatch('highlights/listByCurrent', 'fulltextSearch')
        }
      )
    },
    cancel () {
      this.search.input = ''
    }

  }
}
</script>