<template lang="pug">
  div
    h1 Highlights
    div(v-if="loadingRecords")
      p(style="text-align: center")
        el-button(type="primary" :loading="true" round plain)
    div(v-else="loadingRecords")
      HighlitedListItem(:article="article" v-for="article in records")
</template>

<script>
import HighlitedListItem from './list-item.vue'
import { mapState, mapGetters } from 'vuex'

export default {
  components: {
    HighlitedListItem,
  },
  computed: {
    ...mapState('highlights', ['loadingRecords']),
    ...mapGetters('highlights', [
      'records',
    ]),
  },
  data () {
      return {
          articles: [
              {
                  id:1,
                  title: 'Isolation and characterization of SARS-CoV-2 from the first US COVID-19 patient',
                  authors: ['JHarcourt J', 'Tamin A', 'Lu X', 'Kamili S', 'Sakthivel SK', 'Murray J', 'Queen K', 'Tao Y', 'Paden CR', 'Zhang J', 'Li Y', 'Uehara A', 'Wang H', 'Goldsmith C', 'Bullock HA', 'Wang L', 'Whitaker B', 'Lynch B', 'Gautam G', 'Schindewolf C', 'Lokugamage KG', 'Scharton D', 'Plante JA', 'Mirchandani D', 'Widen SG', 'Narayanan K', 'Makino S', 'Ksiazek TG', 'Plante KS', 'Weaver SC', 'Lindstrom S', 'Tong S', 'Menachery VD', 'Thornburg NJ',],
                  abstract: 'The etiologic agent of the outbreak of pneumonia in Wuhan China was identified as severe acute respiratory syndrome associated coronavirus 2 (SARS-CoV-2) in January, 2020. The first US patient was diagnosed by the State of Washington and the US Centers for Disease Control and Prevention on ract1...',
                  doi: 'https://doi.org/10.1101/2020.03.02.972935',
                  smart_figure: [
                      {
                          img_url: 'https://api.sourcedata.io//file.php?panel_id=17107',
                          legend: 'E, F Fasting bloodglucose (E) and HOMA insulin resistance (IR) index (F) in weight-matched HFD-fed WT-R (n = 5) and NOD2-R (n = 4) mice, 5 weeks after colonization of germ-free mice, *P = 0.02 and **P = 0.0001.',
                          url: 'https://search.sourcedata.io/panel/17117',
                      },
                      {
                          img_url: 'https://api.sourcedata.io//file.php?panel_id=17105',
                          legend: 'C Relative abundance of phyla in the cecum from each recipient mouse.',
                          url: 'https://search.sourcedata.io/panel/17105',
                      },
                  ],
              },
              {
                  id:2,
                  title: 'The inhaled corticosteroid ciclesonide blocks coronavirus RNA replication by targeting viral NSP15',
                  authors: ['Matsuyama S', 'Kawase M', 'Nao N', 'Shirato K', 'Ujike M', 'Kamitani W', 'Shimojima M', 'Fukushi S',],
                  abstract: 'Steroid compounds, which are expected to have dual functions in blocking host inflammation and MERS-CoV replication, were screened from a chemical library. Within this library, ciclesonide, an inhaled corticosteroid, suppressed human coronavirus replication in cultured cells, but did not suppress',
                  doi: 'https://www.biorxiv.org/content/10.1101/2020.03.11.987016v1',
                  smart_figure: [
                      {
                          img_url: 'https://api.sourcedata.io//file.php?panel_id=26947',
                          legend: 'J) Insulin tolerance test was performed in control and Mfn2KO old mice (n=6 mice per group).',
                          url: 'https://search.sourcedata.io/panel/26947',
                      },
                  ],
              },
          ]
      }
  },
}
</script>