<template lang="pug">
  v-card
    v-card-title About: {{ service_name }}
    v-card-subtitle
      a(href:url) {{ url }}
    v-card-text
      v-list
        v-list-item
          p
            b Type of evaluation:
            |
            | {{ (evaluation_type === 'peer_review')? "Formal peer review" : "Commenting" }}
        v-list-item
          p
            b Journal-independent:
            |
            | {{ journal_independent? "Yes" : "No" }}
        v-list-item
          p
            b Post-review certification:
            |
            | {{ certification ? "Makes editorial decisons/recommendations." : " No editorial decisions." }}
        v-list-item
          p
            b Reviewed content:
            |
            | {{ author_driven? "Author-driven submissions." :  "Author-independent curation." }}
</template>

<script>

export default {
  name: "InfoCardsReviewServiceSummary",
  props: {
      service_name: String,
      url: String,
      evaluation_type: String, // "peer_review" | "commenting"
      certification: Boolean, 
      author_driven: Boolean,
      journal_independent: Boolean,
  },
  computed: {
    prop2text_evaluation_type (key){
        const text = {
            peer_review: 'formal in-depth peer review',
            commenting: 'commenting'
        }
        return text[key]
    },
  },
}
</script>

<style lang="scss" scoped>
  .router-link-active {
    color: #FFFFFF;
    background-color: #409EFF;
    border-color: #409EFF;

    &:hover {
      color: #EEE;
    }
  }
</style>