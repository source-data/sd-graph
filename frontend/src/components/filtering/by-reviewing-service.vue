<template lang="pug">
v-card(flat)
  v-card-title Review sources
  v-card-text
    v-chip-group(v-model="selectedReviewers" mandatory column multiple)
      span(v-for="service in this.reviewing_services" :key="`${service.id}-chip`")
        v-chip(:value="service.id" :disabled="loadingRecords" filter filter-icon="mdi-check" 
               active-class="active-chip" text-color="black")
          img(v-if="imageFileName(serviceId2Slug(service.id))" :src="require(`@/assets/chips/` + imageFileName(serviceId2Slug(service.id)))" height="24px" :alt="serviceId2Name(service.id)").pa-1
          | {{ serviceId2Name(service.id) }}
</template>

<script>

import { mapState } from 'vuex'
import { serviceId2Slug, serviceId2Name } from '../../store/by-filters'

export default {
  data () {
    return {}
  },
  computed: {
    ...mapState('byFilters', ['reviewing_services', 'loadingRecords', 'reviewed_bys']),

    selectedReviewers: {
      set(values) {
        this.$store.commit("byFilters/setReviewedBys", values);
        this.$store.commit("byFilters/setCurrentPage", 1);
        this.$store.dispatch('byFilters/updateRecords');
      },
      get() {
        return this.reviewed_bys
      }
    }
  },
  methods: {
    // Returns the filename for the  image that should be associated with the chip's text, or null if none is found
    imageFileName(slug) {
      const availableSourceLogos = require.context('../../assets/chips/', true, /\.(svg|png|jpg)/).keys()
      let filename = availableSourceLogos.find(i => i.includes(slug))
      if (filename)
        return filename.substring(2) // substring to remove the `./` part of the name
      else return null
    },
    serviceId2Slug,
    serviceId2Name
  },
}
</script>

<style lang="scss" scoped>
.active-chip {
  background-color: var(--v-accent-lighten1);
}
</style>