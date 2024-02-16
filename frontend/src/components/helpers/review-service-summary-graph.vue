<template lang="pug">
v-card
  v-card-title
    span(slot)
      h3(v-html="$t('review_service_summary.title_html', {url, name: service_name})")
  v-card-text
    h3.mb-1 {{ $t('review_service_summary.process.title') }}
    v-container.grey.lighten-4.mb-5.rounded-lg
      v-row(v-if="review_requested_by" no-gutters)
        v-row(dense)
          v-col.d-flex.align-center
            b
              span(v-if="review_requested_by==='Authors'") {{ $t('review_service_summary.process.submit.author_driven') }}
              span(v-else) {{ $t('review_service_summary.process.submit.author_independent') }}
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i {{ $t('review_service_summary.process.submit.tooltip.question') }}
                b.ml-1(v-if="review_requested_by==='Authors'") {{ $t('review_service_summary.process.submit.tooltip.answer.author_driven') }}
                b.ml-1(v-else) {{ $t('review_service_summary.process.submit.tooltip.answer.author_independent') }}
      

      v-row(v-if="reviewer_selected_by" no-gutters)
        v-row(dense)
          v-col.d-flex.align-center
            b
              span(v-if="reviewer_selected_by==='Editor, service, or community'") {{ $t('review_service_summary.process.reviewer_selection.service') }}
              span(v-else-if="reviewer_selected_by==='Self-nominated'") {{ $t('review_service_summary.process.reviewer_selection.self') }}
              span(v-else-if="reviewer_selected_by==='Authors'") {{ $t('review_service_summary.process.reviewer_selection.author') }}
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i {{ $t('review_service_summary.process.reviewer_selection.tooltip.question') }}
                b.ml-1(v-if="reviewer_selected_by==='Editor, service, or community'") {{ $t('review_service_summary.process.reviewer_selection.tooltip.answer.service') }}
                b.ml-1(v-else-if="reviewer_selected_by==='Self-nominated'") {{ $t('review_service_summary.process.reviewer_selection.tooltip.answer.self') }}
                b.ml-1(v-else-if="reviewer_selected_by==='Authors'") {{ $t('review_service_summary.process.reviewer_selection.tooltip.answer.author') }}

      v-row(v-if="opportunity_for_author_response" no-gutters)
        v-row(dense)
          v-col.d-flex.align-center
            b
              span(v-if="opportunity_for_author_response=='Included'") {{ $t('review_service_summary.process.author_response.yes') }}
              span(v-else) {{ $t('review_service_summary.process.author_response.no') }}
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i {{ $t('review_service_summary.process.author_response.tooltip.question') }}
                b.ml-1(v-if="opportunity_for_author_response=='Included'") {{ $t('review_service_summary.process.author_response.tooltip.answer.yes') }}
                b.ml-1(v-else) {{ $t('review_service_summary.process.author_response.tooltip.answer.no') }}

      v-row(v-if="recommendation" no-gutters)
        v-row(dense)
          v-col.d-flex.align-center
            b
              span(v-if="recommendation=='Binary decision'") {{ $t('review_service_summary.process.recommendation.binary') }}
              span(v-else-if="recommendation=='Scale or rating'") {{ $t('review_service_summary.process.recommendation.scale') }}
              span(v-else) {{ $t('review_service_summary.process.recommendation.no') }}
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i {{ $t('review_service_summary.process.recommendation.tooltip.question') }}
                b.ml-1 {{ $t('review_service_summary.process.recommendation.tooltip.answer', {recommendation}) }}

    h3.mb-1 {{ $t('review_service_summary.policy.title') }}
    v-container.grey.lighten-4.rounded-lg
      v-row(v-if="peer_review_policy" no-gutters)
        v-row(dense)
          v-col.d-flex.flex-row.align-center
            span {{ $t('review_service_summary.policy.guidelines.title') }}
            b.prd_val(v-html="$t('review_service_summary.policy.guidelines.description_html', {url: peer_review_policy})")

            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i {{ $t('review_service_summary.policy.guidelines.tooltip') }}

      v-row(v-if="review_coverage" no-gutters)
        v-row(dense)
          v-col.d-flex.flex-row.align-center
            span(v-if="review_coverage") {{ $t('review_service_summary.policy.coverage.title') }}
            b.prd_val {{  $t('review_service_summary.policy.coverage.description', {review_coverage}) }}
            v-tooltip(color="tooltip" right transition="fade-transition") 
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i {{ $t('review_service_summary.policy.coverage.tooltip') }}

      v-row(v-if="reviewer_identity_known_to" no-gutters)
        v-row(dense)
          v-col.d-flex.flex-row.align-center
            span(v-if="reviewer_identity_known_to") {{ $t('review_service_summary.policy.identity.title') }}
            b.prd_val {{ $t('review_service_summary.policy.identity.description', {reviewer_identity_known_to}) }}
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i {{ $t('review_service_summary.policy.identity.tooltip') }}

      v-row(v-if="competing_interests" no-gutters)
        v-row(dense)
          v-col.d-flex.flex-row.align-center
            span(v-if="competing_interests==='Checked'") {{ $t('review_service_summary.policy.competing_interests.title') }}
            b.prd_val {{ $t('review_service_summary.policy.competing_interests.description', {competing_interests}) }}
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-2
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span
                i {{ $t('review_service_summary.policy.competing_interests.tooltip.question') }}
                b.ml-1(v-if="competing_interests=='Checked'") {{ $t('review_service_summary.policy.competing_interests.tooltip.answer.yes') }}
                b.ml-1(v-else) {{ $t('review_service_summary.policy.competing_interests.tooltip.answer.no') }}
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