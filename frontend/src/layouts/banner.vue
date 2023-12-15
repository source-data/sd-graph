<template lang="pug">
  .banner-title-wrapper
    v-row.d-flex.flex-grow-1.align-baseline
      span.text-md-h4.text-sm-h5.text-h5.pointer.banner-title
        router-link(to="/"  active-class="is-active")
          | Early Evidence Base
      span.ml-1.text-sm-body-2.text-caption.font-italic.d-none.d-sm-flex.align-end
        span an initiative by
        img(src="../assets/EMBO_logo.svg" alt="EMBO Logo" height="30rem").ml-2
    v-row
      .text-md-h5.text-sm-h6.text-subtitle-2.pointer.banner-subtitle Collecting and Assessing Reviewed Preprints
    v-row.d-flex.d-sm-none
      span.mt-1.text-caption.font-italic.d-flex.align-center
        span an initiative by
        img(src="../assets/EMBO_logo.svg" alt="EMBO Logo" height="20rem").ml-2
</template>

<style lang="scss" scoped>

.banner-title-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  padding: 1.5rem 1.5rem;
}

.banner-title {
  color:#0a5769;
}

.banner-subtitle {
  color:#217b90;
}

</style>