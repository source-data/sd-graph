<template lang="pug">
  v-card(class="pa-5" outlined)
    v-card-title Highlighted topics
    v-card-subtitle Topics and key entities were identified and labeled in an unsupervised way based on the structure of a knowledge graph automatically derived from figure legends.
    v-card-text 
      p
       b Tip:
       |
       | select 
       i 'show results as the intersection between topics (AND)'
       |
       | below to find studies identified in multiple categories
      
      v-item-group(
        v-model="selectedTopics"
        @change="onChange"
        :multiple="(operator !== 'single')"
        mandatory
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
                    i {{ item.entity_highlighted_names.slice(0,10).join(', ') }}
        v-radio-group(
          row
          v-model="operator"
          @change="onChangeOperator"
          active-class="grey lighten-5"
        )
          template(v-slot:label)
            small show results:
          v-radio(value='single').rounded.pa-1
            template(v-slot:label)
              small from a <span class="primary--text">single</span> selected topic
          v-radio(value='and').rounded.pa-1
            template(v-slot:label)
              small as the <span class="primary--text">intersection</span> between topics (AND)
          v-radio(value='or').rounded.pa-1
            template(v-slot:label)
              small as the <span class="primary--text">union</span> across multiple topics (OR)
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
      // default value
      selectedTopics: 0,
      operator: 'single'
    }
  },
  computed: {
    ...mapGetters('byAutoTopics', [
      'records',
    ]),
    autoTopicsList () {
      return this.records.slice(0,15)
    },
  },
  methods: {
    onChange(selectedItemsIds) {
      this.$emit('change', selectedItemsIds)
    },
    onChangeOperator() {
      if (this.operator === 'single' && Array.isArray(this.selectedTopics)) { // transition from multiple selection to single selection
        this.selectedTopics = this.selectedTopics[0]
      } else if (this.operator !== 'single' && !Array.isArray(this.selectedTopics)) { // transition from single selectoin to multiple
        this.selectedTopics = [this.selectedTopics]
      }
      this.$emit('changeOperator', this.operator)
    }
  },
}
</script>

