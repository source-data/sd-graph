<template lang="pug">
  div
    h4 About: {{ service_name }}
    p
      a(href:url) {{ url }}
    p
      ul
        li
          | Type of evaluation:
          |
          b {{ (evaluation_type == "formal_peer_review") ? "Formal peer review" : "Commenting" }}
        li
          | Journal-independent:
          |
          b {{ journal_independent ? "Yes" : "No" }}
        li
          | Post-review certification:
          |
          b {{ certification ? "Makes editorial decisons/recommendations" : "No editorial decisions" }}
        li
          | Reviewed content:
          |
          b {{ author_driven ? "Author-driven submissions." :  "Author-independent curation" }}
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