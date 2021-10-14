<template lang="pug">
  v-card(outlined)
    v-card-title
      span(slot)
        | About: <i>{{ service_name }}</i>
    v-card-subtitle
      a(:href="url" target="_blank" rel="noopener") {{ url }}
    v-card-text
      h4 Process
      v-container.grey.lighten-4.mb-5.rounded-lg
        //-.green--text.text--darken-3
        v-row(v-if="review_requested_by")
          v-col
            span(v-if="review_requested_by==='Authors'") Author-driven
            span(v-else) Author-independent
          v-col(align="center")
            span(v-if="review_requested_by==='Authors'")
              //- v-icon fas fa-book-open
              //- v-icon fas fa-user-graduate
              //- v-icon fas fa-caret-right
              //- v-icon fas fa-building
              v-icon.author mdi-account-tie
              v-icon.preprint mdi-book-open-variant
              v-icon mdi-menu-right
              v-icon.office mdi-office-building-outline
            span(v-else) 
              //-   v-icon fas fa-book-open
              v-icon.office mdi-office-building-outline
              v-icon mdi-menu-left
              v-icon.preprint mdi-book-open-variant
        v-row(v-if="reviewer_selected_by" dense)
          v-col
            span(v-if="reviewer_selected_by==='Editor, service, or community'") Invited reviewers
            span(v-else-if="reviewer_selected_by==='Self-nominated'") Self-nominated reviewers
            span(v-else-if="reviewer_selected_by==='Authors'") Author-selected reviewers
          v-col(align="center")
            span(v-if="reviewer_selected_by==='Editor, service, or community'")
              //-   v-icon fas fa-building
              //- fa-chalkboard-user
              //- <i class="fa-solid fa-book-open-reader"></i>
              //-   v-icon fas fa-caret-right
              //-   v-icon fas fa-users
              v-icon.office mdi-office-building-outline
              v-icon mdi-menu-right  
              v-icon.reviewer mdi-account-group
            span(v-else-if="reviewer_selected_by==='Self-nominated'")
              //-   v-icon fas fa-users
              //-   v-icon fas fa-caret-right
              //-   v-icon fas fa-building
              v-icon.reviewer mdi-account-group
              v-icon mdi-menu-right
              v-icon.office mdi-office-building-outline
            span(v-else-if="reviewer_selected_by==='Authors'")
              //-   v-icon fas fa-graduate-user
              //-   v-icon fas fa-caret-right
              //-   v-icon fas fa-users
              //-   v-icon fas fa-caret-right
              //-   v-icon fas fa-building
              v-icon.author mdi-account-tie
              v-icon mdi-menu-right
              v-icon.reviewer  mdi-account-group
              v-icon mdi-menu-right
              v-icon.office mdi-office-building-outline
        v-row(v-if="public_interaction" dense)
          v-col
            span(v-if="public_interaction=='Included'") Public feedback
            span(v-else) No public interactions
          v-col(align="center")
            span(v-if="public_interaction=='Included'")
              v-icon.crowd mid-crowd
            span(v-else)
              v-icon mdi-minus
        v-row(v-if="opportunity_for_author_response" dense)
          v-col
            span(v-if="opportunity_for_author_response=='Included'") Authors reply
            span(v-else)  No author reply
          v-col(align="center")
            span(v-if="opportunity_for_author_response=='Included'")
              //-   v-icon  fas fa-user-graduate
              //-   v-icon fas fa-caret-right
              //- v-icon fas fa-list
              v-icon.author mdi-account-tie
              v-icon mdi-menu-right
              v-icon.response mdi-message-bulleted
            span(v-else)
              v-icon mdi-minus
              //- i.fas.fa-minus
        v-row(v-if="recommendation" dense)
          v-col
            span(v-if="recommendation=='Binary decision'") Binary decision 
            span(v-else-if="recommendation=='Other scale or rating'") Scaled rating
            span(v-else) No decision
          v-col(align="center")
            span(v-if="recommendation=='Binary decision'")
              //- v-icon fas fa-award
              v-icon.recommendation mdi-certificate
            span(v-else-if="recommendation=='Other scale or rating'")
              //-v-icon fas bar-chart
              //- i.fas.fa-square-poll-horizontal
              v-icon.recommendation mdi-chart-bar
            span(v-else)
              v-icon mdi-minus
              //-v-icon fas fa-minus
      h4 Policy
      v-container.grey.lighten-4.rounded-lg
        //- .red--text.text--darken-4
        v-row(v-if="peer_review_policy" dense)
          v-col
            span Reviewing guidelines:
          v-col
            b.prd_val Yes (
                a(:href="peer_review_policy" target="_blank" rel="noopener") read more
                v-icon(small class="pa-1") mdi-open-in-new
                |)
        v-row(v-if="review_coverage" dense)
          v-col
            span(v-if="review_coverage") Review coverage:
          v-col
            b.prd_val {{ review_coverage }}
        v-row(v-if="reviewer_identity_known_to" dense)
          v-col
            span(v-if="reviewer_identity_known_to") Reviewer identity known to:
          v-col
            b.prd_val {{ reviewer_identity_known_to }}
        v-row(v-if="competing_interests" dense)
          v-col
            span(v-if="competing_interests==='Checked'") Competing interests:
          v-col
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
  .fas {
    font-size: 18px !important;
    padding: 2px;
  }
  .preprint, .author{
    color: #B71C1C !important; // red darken-4
  }
  .office {
    color: #0D47A1 !important; // blue darkent-4
  }
  .reviewer {
    color: #2E7D32 !important; //green darken-3
  }
  .crowd {
    color: #9E9D24 !important; // teal darken-2
  }
  .response {
    color: #512DA8 !important; //deep-purple--text.text--darken-2
  }
  .recommendation {
    color: #F9A825 !important; //yellow--text.text--darken-3

  }
</style>