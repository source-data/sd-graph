<template lang="pug">
  .banner-title-wrapper
    router-link(to="/"  active-class="is-active")
      .text-xl-h2.text-lg-h2.text-md-h3.text-sm-h4.text-h5.pointer.banner-title 
        b Early Evidence Base
        .text-xl-h4.text-lg-h4.text-md-h5.text-sm-h6.text-h6.pointer.banner-subtitle Accessing early scientific findings
</template>

<style lang="scss" scoped>


.banner-title-wrapper {
  padding: 1rem 1rem;
  background-color: rgba(255,255,255,0.75);
  position: absolute;
  top: 3rem;
}

@media screen and (min-width: 600px) {
  .banner-title-wrapper {
    position: absolute;
    top: 3rem;
    left: 80px;
  }
}

@media screen and (min-width: 960px) {
  .banner-title-wrapper {
    position: absolute;
    top: 3rem;
    left: 200px;
  }
}

@media screen and (min-width: 1264px) {
  .banner-title-wrapper {
    position: absolute;
    top: 3rem;
    left: 250px;
  }
}

@media screen and (min-width:1904px) {
  .banner-title-wrapper {
    position: absolute;
    top: 3rem;
    left: 350px;
  }
}

.banner-title {
  color:#0a5769;
}

.banner-subtitle {
  color:#217b90;
}

</style>