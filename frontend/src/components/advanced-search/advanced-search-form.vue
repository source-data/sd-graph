<template lang="pug">
v-card(flat).flex-grow-1
    v-card-title Advanced Search
    v-card-text
    label Search terms
    v-form(v-model="valid")
        v-row(v-for="(term, idx) in searchTerms")
            v-col.col-lg-2.col-md-2.col-sm-4.col-5
                v-select(outlined v-model="term.termType.value" :items="termTypes" :item-value="t => t.value" :item-text="t => t.text" dense hide-details style="max-width: 150px;")
            v-col.col-lg-8.col-md-8.col-sm-7.col-6
                v-text-field(
                    v-model="term.termText"
                    placeholder="Enter term"
                    hide-details
                    outlined
                    dense
                ).mt-0.pt-0
            v-col.col-lg-2.col-md-2.col-sm-1.col-1
                v-tooltip(color="tooltip" bottom transition="fade-transition")
                    template(v-slot:activator="{ on, hover, attrs }")
                        v-btn(text v-bind="attrs" v-on="on" @click="addOrDelete(idx)" icon)
                            v-icon(v-if="idx !== searchTerms.length - 1" dense) mdi-close-circle
                            v-icon(v-else dense) mdi-plus-circle
                    span Clear search term
        
        v-row.ma-0
            v-col.col-lg-8.col-md-8.col-sm-12.col-12.pl-0
                label Reviewed by (leave blank for all)
                v-autocomplete(
                    v-model="selectedReviewers"
                    :items="reviewing_services"
                    :item-value="reviewerValue"
                    :item-text="reviewerText"
                    label="Select reviewers"
                    multiple outlined deletable-chips hide-details
                    chips).mx-0.mt-1

        v-row.ma-0
            v-col.col-lg-8.col-md-8.col-sm-12.col-12.pl-0.pt-0
                label Published in (leave blank for all)
                v-autocomplete(
                    v-model="selectedPublishers"
                    :items="publishers"
                    :item-value="publisherValue"
                    :item-text="publisherText"
                    label="Select publishers"
                    multiple outlined deletable-chips hide-details
                    chips).mx-0.mt-1
        
        v-row.ma-0.d-flex.flex-column
            label Reviewed date
            v-radio-group(v-model="reviewedDate.radio").ml-3
                v-row.d-flex.align-center
                    v-col
                        v-radio(key="0" label="All" value="all").mr-6
                v-row.d-flex.align-center.mt-0
                    v-col.col-lg-6.col-md-8.col-sm-8.col-12
                        v-radio(key="1" label="Last" value="last").mr-6
                        v-select(outlined v-model="reviewedDate.last" :items="lastOptions" dense hide-details).pl-12
                v-row.d-flex.align-center.mt-2
                    v-col.col-lg-6.col-md-6.col-sm-8.col-12
                        v-radio(key="2" label="Custom range" value="custom")
                        span.d-flex.flex-row.pl-12
                            DatePicker(:date="reviewedDate.fromDate" :label="'From'" @dateChanged="value => reviewedDate.fromDate = value")
                            DatePicker(:date="reviewedDate.toDate" :label="'To'" @dateChanged="value => reviewedDate.toDate = value")
        v-row.ma-0.d-flex.flex-column
            label Publication date
            v-radio-group(v-model="publishedDate.radio").ml-3
                v-row.d-flex.align-center
                    v-col
                        v-radio(key="0" label="All" value="all").mr-6
                v-row.d-flex.align-center.mt-0
                    v-col.col-lg-6.col-md-8.col-sm-8.col-12
                        v-radio(key="1" label="Last" value="last").mr-6.mb-2
                        v-select(outlined v-model="publishedDate.last" :items="lastOptions" dense hide-details).pl-12
                v-row.d-flex.align-center.mt-2
                    v-col.col-lg-6.col-md-6.col-sm-8.col-12
                        v-radio(key="2" label="Custom range" value="custom")
                        span.d-flex.flex-row.pl-12
                            DatePicker(:date="publishedDate.fromDate" :label="'From'" @dateChanged="value => publishedDate.fromDate = value")
                            DatePicker(:date="publishedDate.toDate" :label="'To'" @dateChanged="value => publishedDate.toDate = value")

        v-row.ma-0
            v-btn(:disabled="!valid" color="primary" @click="submit").ml-auto Submit search
</template>
    
    <script>
    import { mapState } from 'vuex'
    import DatePicker from '../helpers/date-picker.vue'
    import { serviceId2Name } from '../../store/by-filters'
    
    export default {
      components: {
        DatePicker
      },
      data: function() {
        return {
            valid: true,

            selectedPublishers: [],
            selectedReviewers: [],
            searchTerms: [{termText: "", termType: {text: "Anywhere", value: "anywhere"}}],
            reviewedDate: {
                radio: "all",
                last: "month",
                fromDate: new Date().toISOString().slice(0, 7),
                toDate: new Date().toISOString().slice(0, 7),
            },
            publishedDate: {
                radio: "all",
                last: "month",
                fromDate: new Date().toISOString().slice(0, 7),
                toDate: new Date().toISOString().slice(0, 7),
            },

            termTypes: [{text: "Anywhere", value: "anywhere"}, {text: "Title", value: "text"}, 
                        {text: "Author", value: "author"}, {text: "Institution", value: "institution"}],
            lastOptions: [{text: "month", value: 1}, {text: "6 months", value: 6}, {text: "year", value: 12}],
        }
      },
      computed: {
        ...mapState('byFilters', ['publishers', 'reviewing_services']),
      },
      methods: {
        addOrDelete(idx) {
            if (idx === this.searchTerms.length - 1) {
                this.searchTerms.push({termText: "", termType: {text: "Anywhere", value: "anywhere"}})
            } else {
                this.searchTerms.splice(idx, 1)
            }
        },

        reviewerText(reviewer) {
            return serviceId2Name(reviewer.id)
        },
        reviewerValue(reviewer) {
            return reviewer.id
        },
        publisherText(publisher) {
            return `(${publisher.n_papers}) ${publisher.id}`
        },
        publisherValue(publisher) {
            return publisher.id
        },
        submit() {
            //TODO: Vuex things; could work in a different store, similar to the existing one, or in the same one
        }
      }
    }
    </script>