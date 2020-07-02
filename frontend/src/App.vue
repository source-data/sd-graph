<template lang="pug">
  el-container
    el-header(height="400px").banner_img
      a(href="https://embo.org" target="_blank")
        img(src="./assets/EEB_E_LOGO.png" height="90px" style="margin-top:180px; float: left; transform: translate(0, -50%)")
      a(href="https://embopress.org")
        img(src="./assets/EEB_EP_LOGO.png" width="120px" style="margin-top:16px; margin-left:30px; float:right; transform: translate(0, -50%) ")
      a(href="https://sourcedata.io" target="_blank")
        img(src="./assets/EEB_SD_LOGO.png" width="120px" style="margin-top:16px; float:right; transform: translate(0, -50%) ")
      p(style="position: absolute; top: 120px; left: 840px; min-width: 400px; font-size:24px")
        | Accessing early <br/>scientific findings
      h1(@click="goHome" style="position: absolute; top:290px; left:700px; transform: translate(0, -50%); min-width: 380px").title.pointer Early Evidence Base
    el-container
      el-aside(width="180px" style="border-right-style: solid; border-right-width: 1px; padding-top: 50px")
        el-menu(default-active="1" @select="navigate")
          el-menu-item(index="0") 
            span.el-icon-s-home
            | Home
          el-menu-item(index="1") About
          el-menu-item(index="2" disabled) For developers
          el-menu-item(index="3" disabled) Contact
        el-divider
        div(style="padding:10px")
          small Database stats: 
            p 
              code {{ db_stats.ai_annotated || 0 }}
              |  preprints automatically annotated. 
            p 
              code {{ db_stats.sd_annotated || 0 }}
              |  experiments in the SourceData knowledge graph
            p 
              code {{db_stats.total_nodes || 0 }}
              |  nodes in EBB.
      el-main
        router-view
    el-footer
      el-row
        el-col(:span="16" :offset="4")
          small EMBO 	&#169; {{ thisYear }}

</template>

<script>
import { mapGetters } from 'vuex'
import home from './views/Home.vue'

export default {
  name: 'app',
  components: {
    home,
  },
  methods: {
    goHome() {
        const home_path = "/home"
        if (this.$route.path !== home_path) {
          this.$router.push({path: home_path})
        }
    },
    navigate(key) {
      const paths = {
        '0': '/home',
        '1': '/about',
        '2': '/dev',
        '3': '/contact',
      }
      const selected_path = paths[key]
      if (this.$route.path !== selected_path) {
        this.$router.push({path : selected_path})
      }
    }
  },
  computed: {
    thisYear () {
      return new Date().getFullYear()
    },
    ...mapGetters(['db_stats'])
  },
  beforeCreate () {
    this.$store.dispatch('statsFromFlask').then(
      () => this.$store.commit('incrementInit'))
    this.$store.dispatch('byReviewingService/getAll').then(
      () => {
        this.$store.dispatch('highlights/listByCurrent', 'byReviewingService')
      }
    ).then(
          () => this.$store.commit('incrementInit')
    ),
    this.$store.dispatch('byHyp/getAll').then(
      () => this.$store.commit('incrementInit')
    ),
    this.$store.dispatch('byAutomagic/getAll').then(
      () => this.$store.commit('incrementInit')
    ),
    this.$store.commit('highlights/updateSelectedTab', 'byReviewingService')
  },
}
</script>

<style scoped lang="scss">
#header {
  border-bottom-style: solid;
  border-bottom-width: 1px;
}

.title {
  font-size: 36px;
  font-style: normal !important;
  font-family: 'Open Sans', Arial, sans-serif;
}

.banner_img {
  background-image: url("./assets/EEB_HP_Banner.jpg");
  background-size:cover;
}

.pointer {
   cursor: pointer;
}

img.center-img {
  display: block;
  margin-left: auto;
  margin-right: auto;
}

.vertical-align {
  margin-top: 80px;
  transform: translate(0, -50%) 
}

.side_bar_links {
  padding-left: 25px;
}
</style>


