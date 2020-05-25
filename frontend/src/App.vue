<template lang="pug">
  el-container
    el-header(height="120px")#header
      el-col(:span="4")
        p
          a(href="https://embo.org" target="_blank" )
            img(src="./assets/EMBO_logo_RGBmonoblack_outlined.jpg" height="80px").center-img
      el-col(:span="16")
        h1(style="text-align: center") Early Evidence Base: SARS-CoV-2
        p(style="text-align: center") A structured resource of early results on the biology of SARS-CoV-2
      el-col(:span="4")
        p 
          a(href="https://sourcedata.io" target="_blank" )
            img(src="./assets/sourcedata_logo_rgb.png" width="200px").center-img
        //p 
        //  img(src="./assets/embopress_logo_cmyk.jpg" width="120px").center-img
    el-main
      el-row
        el-col(:span="16" :offset="4")
          p This resource prioritizes preprints with experimental results related to the biology of the virus SARS-CoV-2. The resource is developed by EMBO SourceData.
          el-divider
      el-row
        el-col(:span="16" :offset="4")
          SearchBar(@submit="onSubmit")
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
  methods: {
    onSubmit(query) {
      this.$store.dispatch('fulltextSearch/search', query).then(
        () => {
          // this.$store.commit('fulltextSearch/showRecord', { id: 'search_results' }) // bogus id, but oh well...
          this.$store.dispatch('highlights/listByCurrent', 'fulltextSearch')
        }
      )
    }
  },
  beforeCreate () {
    this.$store.dispatch('byMethod/getAll'),
    this.$store.dispatch('byMol/getAll'),
    this.$store.dispatch('byHyp/getAll'),
    this.$store.dispatch('byAutomagic/getAll')
  },
}
</script>

<style scoped lang="scss">
#header {
   border-bottom-style: solid;
   border-bottom-width: 1px;
}

img.center-img {
  display: block;
  margin-left: auto;
  margin-right: auto;
}
</style>


