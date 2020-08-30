<template lang="pug">
  v-card(class="pa-5" outlined)
    p Search titles, abstract, figure legends,author name, doi
    v-text-field(
      v-model="query"
      outlined
      clearable
      placeholder="keywords, authors, doi"
      append-outer-icon="mdi-magnify"
      @keyup.enter="onSubmit"
    )
</template>

<script>

export default {
  data: function() {
    return {
      query: ''
    }
  },
  methods: {
    onSubmit()  {
      console.log("submitting", this.query)
      this.$emit('submit', this.query)
    },
  }
}
</script>