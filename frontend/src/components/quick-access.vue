<template lang="pug">
  div
    h1 Quick Access
    el-tabs(type="border-card")
        el-tab-pane(label="By Method")
            el-radio-group
                el-radio(:label="3") X-ray crystallography Assay
                br
                el-radio(:label="6") Pseudovirus Entry Assay
                br
                el-radio(:label="9") Cryo-Electron Microscopy
                br
                el-radio(:label="9") Protein Interaction Assay
                br
                el-radio(:label="9") Dose-responses
                br
        el-tab-pane(label="By Molecule") By Molecule filters
        el-tab-pane(label="By observation and tested hypothesis") By observation and tested hypothesis filters
</template>