<template lang="pug">
  v-card(class="pa-5" outlined)
    v-card-title Highlighted topics
    v-card-subtitle Topics and key entities were identified in an unsupervised way based on the structure of a knowledge graph automatically derived from figure legends.
    v-card-text 
      i <b>Tip</b>: select 'multi-selection as overlap (AND)' below to find studies identified in multiple categories
      
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
                    i {{ item.entity_highlighted_names.join(', ') }}
        v-radio-group(
          row
          v-model="operator"
          @change="onChangeOperator"
        )
          v-radio(value='single' label='single selection')
          v-radio(value='and' label='multi-selection as overlap (AND)')
          v-radio(value='or' label='multi-slection as union (OR)')
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
      return this.records.slice(0,12)
    },
  },
  methods: {
    onChange(selectedItemsIds) {
      this.$emit('change', selectedItemsIds)
    },
    onChangeOperator(value) {
      if (value === 'single') {this.selectedTopics = this.selectedTopics[0]}
      this.$emit('changeOperator', value)
    }
  },
}
</script>

