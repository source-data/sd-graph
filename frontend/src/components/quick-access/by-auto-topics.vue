<template lang="pug">
  v-card(class="pa-5" outlined)
    v-card-title Recent hypotheses tested in preprints related to SARS-CoV-2/COVID-19.
    v-btn-toggle(v-for="item in autoTopicsList" :key="item.id" @change="onSelect" v-model="selectedTopic")
       v-btn(:value="item.id" small text class="ma-1")
          h3{{item.topics}}
          v-chip(v-for="(entity_name), index) in item.highlighted_entities" :key="`ctrl-${index}`" color="red lighten-3" x-small) {{ entity_name }}
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
      // default value
      selectedTopic: 0
    }
  },
  computed: {
    ...mapGetters('byAutoTopics', [
      'records',
    ]),
    autoTopicsList () {
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

