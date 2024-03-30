<script setup>
import VuePdfEmbed from 'vue-pdf-embed'
import route from "@/router.js";
// essential styles
import 'vue-pdf-embed/dist/style/index.css'
import 'vue-pdf-embed/dist/style/annotationLayer.css'
import 'vue-pdf-embed/dist/style/textLayer.css'
import {useRoute} from "vue-router";
import {onMounted, ref} from "vue";

const router = useRoute()
let source = ref(0)
onMounted(() => {
  source.value = router.params.pdfUrl
  source.value = "http://127.0.0.1:8000/preview?" + source.value
})
// onMounted(() => {
//   // getPagesNumber()
// })
</script>
<template>
  <div class="pdf-wrapper">
    <vue-pdf-embed ref="pdfRef" :source="source"/>
    </div>
</template>

<style scoped>

</style>