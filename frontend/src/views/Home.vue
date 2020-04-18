<template lang="pug">
  div
    //- <img alt="Vue logo" src="../assets/logo.png">
    h1 by Molecule
    pre {{ by_molecule }}
</template>

<script>
import httpClient from '../lib/http'

export default {
  data () {
    return {
      by_molecule: [],
    }
  },
  mounted () {
    httpClient.get('/api/v1/by_molecule')
      .then((response) => {
        console.debug("yeah baby!!", response)
        this.by_molecule = response.data
      })
  }
}
</script>

<style lang="scss">


</style>
