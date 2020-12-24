<template lang="pug">
  v-card(outlined)
    v-card-title
      span(slot)
        | About: <i>{{ service_name }}</i>
    v-card-subtitle
      a(href:url) {{ url }}
    v-card-text
      ul
        //- li
        //-   span(slot).blue--text Formal peer review:
        //-   | &nbsp;
        //-   b {{ (evaluation_type == "formal_peer_review") ? "Yes" : "No" }}
        li
          span(v-if="journal_independent").lime--text.text--darken-4
            | Journal-independent: <b>Yes</b>
          span(v-else) Journal-independent: No
        li
          span(v-if="certification").amber--text.text--darken-4
            | Post-review certification: <b>Yes</b>
          span(v-else) Post-review certification: No
        li
          span(v-if="author_driven").purple--text.text-darken-2
            | Author driven submissions: <b>Yes</b>
          span(v-else) Author-driven submissions: No
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