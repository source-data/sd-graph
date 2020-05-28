<template lang="pug">
  div
    el-row(v-if="article")
      el-row()
        el-col(:span="24")
            h3 {{ article.title }} 
            el-row(type="flex" justify="space-between")
              small() Posted 
                b {{ display_date(article.pub_date) }}
                |  on 
                i {{ display_journal(article.journal) }}
                b  doi:  
                el-link(type="primary" :href="full_url(article.doi).href" target="_blank") http://doi.org/{{ article.doi }} 
            p
              small {{ author_list }}
      el-row()
        el-col(:span="10")
          small(style="line-height:1.5") {{ article.abstract }}
        el-col(:span="2")
          p
        el-col(:span="12")
          label(for="info-cards") {{ info.length }} information cards:
          el-collapse(id="infor-cards" v-model="activeCards")
            el-collapse-item(v-for="card in info"  :title="'for debugging : ' + card.id", :name="card.id" @change="debugCards")
              small {{ card.text }}
          
          //- el-carousel(indicator-position="outside" arrow="hover" :autoplay="false" height="" id="info-cards")
          //-   el-carousel-item(v-for="card in info" :key="card.id" style="text-align:left")
          //-     el-card(class="box-card" shadow="always")
          //-       small {{ card.text }}
            //- a(:href="panel.url")
            //-   el-image(:src="panel.img_url" fit="contain")
            //- p
            //-   a(:href="panel.url") Open in SmartFigure
    el-divider
</template>
<script>
export default {
  props: {
    article: Object,
  },
  data() {
    return {
      activeCards: [this.article.info[0].id]
    }
  },
  methods: {
      debugCards(val) {console.debug("card", val)},
      full_url (doi) {
          return new URL(doi, "https://doi.org/")
      },
      display_date(date_str) {
          const date = new Date(date_str)
          const year = date.getFullYear()
          const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
          const month = months[date.getMonth()]
          const day = date.getDay()
          return month + ' ' + day + ', ' + year 
      },
      display_journal(key) {
        const journal_labels = {
          biorxiv: 'bioRxiv', medrxiv: 'medRxiv'
        }
        return journal_labels[key]
      }
  },
  computed: {
    author_list () {
      return this.article.authors.map(author => `${author.surname} ${author.given_names}${(author.corresp=='yes'?'*':'')}`).join(', ')
    },
    info () {
      return this.article.info
        // .panel_ids.map((panel_id) => {
        //   return {
        //     id: panel_id,
        //     img_url: `https://api.sourcedata.io//file.php?panel_id=${panel_id}`,
        //     url: `https://search.sourcedata.io/panel/${panel_id}`,
        //   }
        // })
    },
  },
}
</script>