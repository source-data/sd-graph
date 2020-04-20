<template lang="pug">
  div
    el-row(v-if="article")
      el-col(:span="12")
        h4 {{ article.title}}
        small
          em {{ authorList }}
        br
        small
          a(:href="article.doi") {{ article.doi }}
        p {{ article.abstract }}
      el-col(:span="12")
        el-carousel(indicator-position="outside" :autoplay="false" height="")
          el-carousel-item(v-for="panel in panels" :key="panel.id" style="text-align:center")
            a(:href="panel.url")
              el-image(:src="panel.img_url" fit="contain")
            p
              a(:href="panel.url") Open in SmartFigure
    el-divider
</template>
<script>
export default {
  props: {
    article: Object,
  },
  computed: {
    authorList () {
      return this.article.authors.map(author => `${author[0]} ${author[1]}`).join(', ')
    },
    panels () {
      return this
        .article
        .panel_ids.map((panel_id) => {
          return {
            id: panel_id,
            img_url: `https://api.sourcedata.io//file.php?panel_id=${panel_id}`,
            url: `https://search.sourcedata.io/panel/${panel_id}`,
          }
        })
    },
  },
}
</script>