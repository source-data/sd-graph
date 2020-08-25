<template lang="pug">
  header.banner-area
    img(src="../assets/EEB_HP_Banner.svg").banner-image
    .banner-title-wrapper
      router-link(to="/"  active-class="is-active")
        h1.title.pointer.banner-title Early Evidence Base
      h3.banner-subtitle Accessing early scientific findings
</template>

<style lang="scss" scoped>
.banner-image {
  display:none;
}

@media screen and (min-width:680px) {
  .banner-image {
    display:block;
    width:100%;
  }
}

.banner-area {
  position:relative;
  display:block;
  background-image: url("../assets/EEB_HP_Banner.svg");
  background-size:cover;
}

@media screen and (min-width:680px) {
  .banner-area {
    position:relative;
    display:flex;
    align-items:center;
    background-image:none;
  }
}


.banner-title-wrapper {
  padding: 2rem 2rem;
  background-color: rgba(255,255,255,0.75);
}

@media screen and (min-width:680px) {
  .banner-title-wrapper {
    position: absolute;
    // top:2rem;
    left:180px;
    padding: 2rem 2rem;
    background-color: rgba(255,255,255,0.75);
  }
}

@media screen and (min-width:1080px) {
  .banner-title-wrapper {
      left: 180px;
  }
}

@media screen and (min-width:1160px) {
  .banner-title-wrapper {
    padding: 4rem 2rem;
  }
}

@media screen and (min-width:1800px) {
  .banner-title-wrapper {
    padding: 6rem 3rem;
  }
}

.banner-title {
  color:#0a5769;
  font-size: 2.5rem;
  line-height:1;

  margin:0 0 1rem 0;
}

.banner-subtitle {
  color:#217b90;
  font-size: 1.5rem;
  line-height:1;

  margin:0 0 0 0;
}

@media screen and (min-width:1080px) {
  .banner-title {
    font-size: 5rem;

  }

  .banner-subtitle {
    font-size: 2rem;

  }
}

@media screen and (min-width:1690px) {
  .banner-title {
    font-size: 6rem;
  }

  .banner-subtitle {
    font-size:3rem;
  }
}


@media screen and (min-width:680px) {
  .banner-logo--press,
  .banner-logo--sourcedata {
    max-height:none;
  }
}

.banner_img {
  background-image: url("../assets/EEB_HP_Banner.svg");
  background-size:cover;
}

</style>