<template lang="pug">
  el-container
    el-header(height="200px")#header
      el-col(:span="4")
        div.vertical-align
          p
            a(href="https://embo.org" target="_blank" )
              img(src="./assets/embo-logo.gif" height="80px").center-img
      el-col(:span="16")
        div.vertical-align
          h1(style="text-align: center" @click="goHome").pointer Early Evidence Base - Refereed Preprints
      el-col(:span="4")
        div.vertical-align
          p 
            a(href="https://sourcedata.io" target="_blank" )
              img(src="./assets/sourcedata-logo.png" width="200px").center-img
          p
            a(href="https://embopress.org")
              img(src="./assets/embopress-logo.jpg" width="200px").center-img
    el-container
      el-aside(width="170px" style="border-right-style: solid; border-right-width: 1px; padding-top: 50px")
        el-menu(default-active="1" @select="navigate")
          el-menu-item(index="0") 
            span.el-icon-s-home
            | Home
          el-menu-item(index="1") About
          el-menu-item(index="2" disabled) For developers
          el-menu-item(index="3" disabled) Contact
        el-divider
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
      const selected_route = paths[key]
      console.debug("path", this.$route.path)
      if (this.$route.path !== selected_route) {
        this.$router.push({path : selected_route})
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
    this.$store.dispatch('byReviewingService/getAll'),
    //this.$store.dispatch('byMethod/getAll'),
    //this.$store.dispatch('byMol/getAll'),
    this.$store.dispatch('byHyp/getAll'),
    this.$store.dispatch('byAutomagic/getAll')
    this.$store.dispatch('statsFromFlask')
  },
}
</script>

<style scoped lang="scss">
#header {
   border-bottom-style: solid;
   border-bottom-width: 1px;
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


