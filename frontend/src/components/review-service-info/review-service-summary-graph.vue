<template lang="pug">
v-card
  v-card-title
    span(slot)
      h3 About 
        a(:href="url" target="_blank" rel="noopener") {{ service_name }}
          
  v-card-text
    h3.mb-1 Process
    v-container.grey.lighten-4.mb-5.rounded-lg
      v-row(v-if="review_requested_by" no-gutters)
        v-row(dense)
          v-col.d-flex.align-center
            b
              span(v-if="review_requested_by==='Authors'") Author-driven
              span(v-else) Author-independent
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i Who submitted the manuscript or initiated the feedback process? 
                b.ml-1 {{ review_requested_by }}.
      

      v-row(v-if="reviewer_selected_by" no-gutters)
        v-row(dense)
          v-col.d-flex.align-center
            b
              span(v-if="reviewer_selected_by==='Editor, service, or community'") Service-selected reviewers
              span(v-else-if="reviewer_selected_by==='Self-nominated'") Self-nominated reviewers
              span(v-else-if="reviewer_selected_by==='Authors'") Author-selected reviewers
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i Who selects the reviewers? 
                b.ml-1 {{ reviewer_selected_by }} select the reviewers.

      v-row(v-if="public_interaction" no-gutters)
        v-row(dense)
          v-col.d-flex.align-center
            b
              span(v-if="public_interaction=='Included'") Public feedback
              span(v-else) No public interactions
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i Was there an opportunity for the public to engage as an integral part of the process? 
                b.ml-1 {{ public_interaction }}.

      v-row(v-if="opportunity_for_author_response" no-gutters)
        v-row(dense)
          v-col.d-flex.align-center
            b
              span(v-if="opportunity_for_author_response=='Included'") Authors reply
              span(v-else)  No author reply
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i Was the author’s response included as an integral part of the process?  
                b.ml-1 {{ opportunity_for_author_response }}.

      v-row(v-if="recommendation" no-gutters)
        v-row(dense)
          v-col.d-flex.align-center
            b
              span(v-if="recommendation=='Binary decision'") Binary decision 
              span(v-else-if="recommendation=='Other scale or rating'") Scaled rating
              span(v-else) No decision
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i Does the service provide a decision/recommendation or a scalar rating after the review process?   
                b.ml-1 Recommendation provided: {{ recommendation }}.

    h3.mb-1 Policy
    v-container.grey.lighten-4.rounded-lg
      v-row(v-if="peer_review_policy" no-gutters)
        v-row(dense)
          v-col.d-flex.flex-row.align-center
            span Reviewing guidelines:
            b.prd_val 
              | Yes
              | (
              a(:href="peer_review_policy" target="_blank" rel="noopener") read more
              | )

            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i Explicit guidelines for reviewers 

      v-row(v-if="review_coverage" no-gutters)
        v-row(dense)
          v-col.d-flex.flex-row.align-center
            span(v-if="review_coverage") Review coverage:
            b.prd_val {{ review_coverage }}
            v-tooltip(color="tooltip" right transition="fade-transition") 
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i Does the feedback cover the entire paper or only a certain section or aspect?

      v-row(v-if="reviewer_identity_known_to" no-gutters)
        v-row(dense)
          v-col.d-flex.flex-row.align-center
            span(v-if="reviewer_identity_known_to") Reviewer identity known to:
            b.prd_val {{ reviewer_identity_known_to }}
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i Are the identities of reviewers known to everyone (public), editors or service, or no one?

      v-row(v-if="competing_interests" no-gutters)
        v-row(dense)
          v-col.d-flex.flex-row.align-center
            span(v-if="competing_interests==='Checked'") Competing interests:
            b.prd_val {{ competing_interests }}
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i Is a declaration of competing interest required?
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
    margin-left: 10px;
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