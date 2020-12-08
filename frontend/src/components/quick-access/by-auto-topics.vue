<template lang="pug">
  v-card(class="pa-5" outlined)
    v-card-title Highlighted topics
    v-card-text 
      p Topics and key entities were identified in an unsupervised way based on the structure of a knowledge graph automatically derived from figure legends.
      i <b>Tip</b>: selecting 2 or more topics will select papers that belong to all selected (AND operation)
      v-item-group(
        v-model="selectedTopics"
        @change="onChange"
        mandatory
        multiple
        active-class="blue-grey lighten-5 teal--text text--darken-1"
      )
        v-container
          v-row(no-gutters)
            v-col(:cols="4"
              v-for="item in autoTopicsList" 
              :key="item.id"
            )
              v-item(v-slot="{active, toggle}").pointer
                div(@click="toggle").pa-2
                  h4 {{item.topics.slice(0, 3).join(', ')}}
                  small
                    i {{ item.entity_highlighted_names.join(', ') }}
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
      // default value
      selectedTopics: [0]
    }
  },
  computed: {
    ...mapGetters('byAutoTopics', [
      'records',
    ]),
    autoTopicsList () {
      return this.records.slice(0,12)
    },
  },
  methods: {
    onChange(selectedItemsIds) {
      this.$emit('change', selectedItemsIds)
    }
  },
}
</script>

