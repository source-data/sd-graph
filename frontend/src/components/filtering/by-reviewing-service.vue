<template lang="pug">
v-card(flat)
  v-card-title Review sources
  v-card-text
    v-chip-group(v-model="selectedReviewers" mandatory column multiple)
      span(v-for="service in this.reviewing_services" :key="`${service.id}-chip`")
        v-chip(:value="service.id" :disabled="loadingRecords" filter filter-icon="mdi-check" outlined
               active-class="active-chip" text-color="black")
          img(v-if="imageFileName(service.id)" :src="require(`@/assets/partner-logos/` + imageFileName(service.id))" height="24px" :alt="serviceId2Name(service.id)").pa-1
          | {{ serviceId2Name(service.id) }}
</template>

<script>

import { mapState } from 'vuex'
import { normalizeServiceName, serviceId2Name } from '../../store/by-filters'

export default {
  data () {
    return {}
  },
  computed: {
    ...mapState('byFilters', ['reviewing_services', 'loadingRecords', 'reviewed_bys']),

    selectedReviewers: {
      set(value) {
        this.$store.commit("byFilters/setReviewedBys", value);
      },
      get() {
        return this.reviewed_bys
      }
    }
  },
  methods: {
    // Returns the filename for the  image that should be associated with the chip's text, or null if none is found
    imageFileName(id) {
      const availableSourceLogos = require.context('../../assets/partner-logos/', true, /\.(svg|png|jpg)/).keys()

      let normalizedServiceName = normalizeServiceName(serviceId2Name(id))
      let filename = availableSourceLogos.find(i => i.includes(normalizedServiceName))
      if (filename)
        return filename.substring(2) // substring to remove the `./` part of the name
      else return null
    },
    normalizeServiceName,
    serviceId2Name
  },
}
</script>

<style lang="scss" scoped>
.active-chip {
  background-color: var(--v-accent-lighten1);
}
</style>