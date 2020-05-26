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
              small {{ authorList }}
      el-row()
        el-col(:span="10")
          small(style="line-height:1.5") {{ article.abstract }}
        el-col(:span="2")
          p
        el-col(:span="12")
          label(for="carousel") {{ info.length }} information cards:
          el-carousel(indicator-position="outside" arrow="hover" :autoplay="false" height="" id="carousel")
            el-carousel-item(v-for="card in info" :key="card.id" style="text-align:left")
              el-card(class="box-card" shadow="always")
                small {{ card.text }}
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
  methods: {
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
    authorList () {
      return this.article.authors.map(author => `${author[0]} ${author[1]}`).join(', ')
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