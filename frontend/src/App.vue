<template lang="pug">
  //- <div id="app">
  //-   <img src="./assets/logo.png">
  //-     <router-link to="/home">Home</router-link> |
  //-     <router-link to="/about">About</router-link>
  //-   <div>
  //-     <p>
  //-       If Element is successfully added to this project, you'll see an
  //-       <code v-text="'<el-button>'"></code>
  //-       below
  //-     </p>
  //-     <el-button>el-button</el-button>
  //-   </div>
  //-   <HelloWorld msg="Welcome to Your Vue.js App"/>
  //- </div>

  el-container
    el-header#header
      el-row
        el-col(:span="4")
          img(src="./assets/embo-logo.png" height="60px")

        el-col(:span="16")
          h1 Early Evidence Base: SARS-CoV-2
          p A structured resource of early results on the biology of SARS-CoV-2
        el-col(:span="4")
          p powered by:
          p
            img(src="./assets/embo-press-logo.png" width="80px")
          p
            img(src="./assets/sourcedata-logo.jpg" width="80px")
    el-divider
    el-main
      el-row
        el-col(:span="16" :offset="4")
          p This resource is dedicated to curated experimental results extracted from preprints related to the biology of the virus SARS-CoV-2. The resource is maintained by EMBO Press editors and SourceData curators and the scientific content is supervised by a board of experts in virology.
          el-divider
      el-row
        el-col(:span="16" :offset="4")
          SearchBar
      el-row
        el-col(:span="16" :offset="4")
          QuickAccess
      el-row
        el-col(:span="16" :offset="4")
          Highlights
    el-footer
      el-row
        el-col(:span="16" :offset="4")
          small EMBO 	&#169; {{thisYear}}

</template>

<script>
import SearchBar from './components/search-bar.vue'
import QuickAccess from './components/quick-access/index.vue'
import Highlights from './components/highlights/index.vue'

export default {
  name: 'app',
  components: {
    SearchBar,
    QuickAccess,
    Highlights,
  },
  computed: {
    thisYear () {
      return new Date().getFullYear()
    },
  },
  beforeCreate () {
    this.$store.dispatch('byMethod/getAll')
    this.$store.dispatch('byMol/getAll')
    this.$store.dispatch('byHyp/getAll')
  },
}
</script>

<style lang="scss">
#header {
  h1 {
    margin:0;
  }
  p {
    margin:0;
  }
}
</style>
