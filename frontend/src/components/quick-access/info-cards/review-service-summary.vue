<template lang="pug">
  v-card(outlined)
    v-card-title
      span(slot)
        | About: <i>{{ service_name }}</i>
    v-card-subtitle
      a(:href="url" target="_blank" rel="noopener") {{ url }}
    v-card-text
      div.lime--text.text--darken-4
        h4 Process
        ul
          li
            span(v-if="review_requested_by")
              | Review requested by: 
              b.prd_val {{ review_requested_by }}
          li
            span(v-if="reviewer_selected_by==='Editor, service, or community'")
              | Reviewer selected by:
              |
              b.prd_val Platform
            span(v-else-if="reviewer_selected_by==='Authors'")
              | Reviewer selected by: 
              |
              p.prd_val Authors
            span(v-else-if="reviewer_selected_by==='Self-nominated'")
              b.prd_val Self-appointed
              | 
              | reviewers
            span(v-else)
              | Reviewer selected by: 
              |
              p.prd_val {{ reviewer_selected_by }}
          li
            span(v-if="public_interaction==='Included'")
              | Public interactions included:
              |
              b.prd_val Yes
            span(v-else)
              | Public interactions included:
              |
              b.prd_val No
          li
            span(v-if="opportunity_for_author_response==='Included'")
              | Authors invited to respond: 
              |
              b.prd_val Yes
            span(v-else)
              | Authors invited to respond
              |
              b.prd_val No
          li
            span(v-if="recommendation=='Binary decision'")
              | Post-review decision:
              |
              b.prd_val Yes
            span(v-else-if="recommendation=='Other scale or rating'")
              | Post-review recommendation:
              |
              b.prd_val Scale or rating
            span(v-else)
              | Post-review recommendation:
              |
              b.prd_val No
      div.purple--text.text--lighted-2
        h4 Policy
        ul
          li
            span(v-if="peer_review_policy")
              | Peer review guidelines:
              | 
              b.prd_val Yes (
                a(:href="peer_review_policy" target="_blank" rel="noopener") read more
                  v-icon(small class="pa-1") mdi-open-in-new
                | )
          li
            span(v-if="review_coverage")
              | Reviewer coverage:
              |
              b.prd_val {{ review_coverage }}
          li
            span(v-if="reviewer_identity_known_to")
              | Reviewer identity known to: 
              b.prd_val {{ reviewer_identity_known_to }}
          li
            span(v-if="competing_interests==='Checked'")
              | Competing interests checked:
              |
              b.prd_val {{ competing_interests }}
</template>

<script>

export default {
  name: "InfoCardsReviewServiceSummary",
  props: {
    service_name: String,
    url: String,
    peer_review_policy: String,
    review_requested_by: String,
    reviewer_selected_by: String,
    review_coverage: String,
    reviewer_identity_known_to: String,
    competing_interests: String,
    public_interaction: String,
    opportunity_for_author_response: String,
    recommendation: String,
  },
}
</script>

<style lang="scss" scoped>
  .prd_val {
    color: #363636;
  }
</style>