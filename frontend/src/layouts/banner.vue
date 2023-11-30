<template lang="pug">
  .banner-title-wrapper
    router-link(to="/"  active-class="is-active")
      .text-sm-h4.text-h5.pointer.banner-title 
        b Early Evidence Base
        .text-sm-h5.text-h6.pointer.banner-subtitle Aggregating Reviewed Preprints
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