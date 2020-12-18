<template lang="pug">
  v-card(class="pa-5" outlined)
    v-card-title Search titles, abstract, figure legends,author name, doi
    v-card-text
      v-container
        v-row(align="center")
          v-col()
            v-text-field(
              v-model="query"
              outlined
              clearable
              :loading="loadingRecords"
              placeholder="keywords, authors, doi"
              prepend-icon="mdi-magnify"
              hide-details
              @keyup.enter="onSubmit"
            )
          v-col()
            v-btn(
              @click="onSubmit"
              color="primary"
            ) Search
</template>

<script>
import { mapState } from 'vuex'
export default {
  data: function() {
    return {
      query: ''
    }
  },
  computed: {
    ...mapState('fulltextSearch', ['loadingRecords'])
  },
  methods: {
    onSubmit()  {
      this.$emit('submit', this.query)
    },
  }
}
</script>