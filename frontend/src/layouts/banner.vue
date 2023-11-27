<template lang="pug">
  .banner-title-wrapper
    router-link(to="/"  active-class="is-active")
      .text-sm-h4.text-h5.pointer.banner-title.d-flex.align-center
        span Early Evidence Base
        div.ml-auto
          span.text-body-2.font-italic an initiative by
          img(src="../assets/EMBO_logo.svg" alt="EMBO Logo" height="30px").ml-2
      .text-sm-h5.text-h6.pointer.banner-subtitle Collecting and Assessing Reviewed Preprints
</template>

<style lang="scss" scoped>

.banner-title-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  padding: 1rem 2rem;
}

.banner-title {
  color:#0a5769;
}

.banner-subtitle {
  color:#217b90;
}

</style>