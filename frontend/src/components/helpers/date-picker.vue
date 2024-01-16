<template lang="pug">
v-menu(
    ref="menu"
    v-model="menu"
    :close-on-content-click="false"
    :return-value.sync="dateVal"
    max-width="290px")

    template(v-slot:activator="{ on, attrs }")
        v-text-field(
            v-model="dateVal"
            :label="label"
            prepend-icon="mdi-calendar"
            readonly
            v-bind="attrs"
            v-on="on")
    v-date-picker(
        v-model="dateVal"
        type="month"
        no-title
        scrollable)
        
        v-spacer
        v-btn(
            text
            color="primary"
            @click="menu = false") Cancel

        v-btn(text color="primary" @click="$refs.menu.save(dateVal)") OK
</template>

<script>
export default {
    data: () => ({
        menu: false
    }),
    props: ['date', 'label'],
    computed: {
        dateVal: {
            get() {
                return this.date;
            },
            set(val) {
                this.$emit('dateChanged', val);
            }
        }
    }
}
</script>