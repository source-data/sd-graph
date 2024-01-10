<template lang="pug">
v-snackbar(v-model='show' :top="true" :color='color' timeout="3000" centered)
  b {{ message }}
  template(v-slot:action="{ attrs }")
    v-btn(
      text
      v-bind="attrs"
      @click="show = false" icon)
        v-icon mdi-close
</template>

<script>
  import { mapState } from 'vuex'

  export default {
    data() {
      return {
        show: false,

        message: "",
        color: ""
      };
    },
    computed: {
      ...mapState(['snackMessage', 'snackColor']),
    },
    watch: {
      snackMessage(nv, ov) {
        if (nv != "" && nv != ov) {
          this.show = true;
          this.message = this.$t(this.snackMessage);
          this.color = this.snackColor;

          this.$store.commit("setSnack", { message: "", color: "" });
        }
      }
    }
  };
</script>