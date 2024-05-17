<script setup>
import {onMounted, reactive, ref} from "vue";

const data = reactive(
    {
      isAndroid: false,
      isIos: false,
      test: 1
    }
)
onMounted( () => {
})
const herfToHome = () => {
  window.location.href = "https://print.233kun.top"
}

</script>
<template>
  <div class="wrapper">
    <div class="href-button">
      <n-button type="info" class="upload-button" @click="herfToHome()">
        <a class="button-text">点击前往打印</a>
      </n-button>
    </div>
  </div>
</template>
<style scoped>
.wrapper {
  display: flex;
  flex-direction: column;
}
.href-button {
  display: flex;
  height: auto;
  justify-content: center;
  min-width: 100%;
}
</style>