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
  const UA = navigator.userAgent
  data.isIos = UA.indexOf("ios") !== -1
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
    <a class="text">打印前先把要打印的文件保存到本地</a>
    <div v-if="data.isIos === false" class="Android">
      <img src="https://47.106.100.54:8000/img/android_tutorial/1.jpg" class="img"/>
      <img src="https://47.106.100.54:8000/img/android_tutorial/2.jpg" class="img"/>
      <img src="https://47.106.100.54:8000/img/android_tutorial/3.jpg" class="img"/>
    </div>
    <div v-if="data.isIos === true" class="iPhone">
      <img src="https://47.106.100.54:8000/img/ios_tutorial/1.jpg" class="img"/>
      <img src="https://47.106.100.54:8000/img/ios_tutorial/2.jpg" class="img"/>
      <img src="https://47.106.100.54:8000/img/ios_tutorial/3.jpg" class="img"/>
      <img src="https://47.106.100.54:8000/img/ios_tutorial/4.jpg" class="img"/>
      <img src="https://47.106.100.54:8000/img/ios_tutorial/5.jpg" class="img"/>
    </div>
    <a class="text">接下来点击蓝色按钮跳转到打印页面，选择你的文件即可打印</a>
  </div>
</template>
<style scoped>
.wrapper {
  display: flex;
  flex-direction: column;
}
.text {
  width: 90%;
  margin-top: 20px;
  margin-left: auto;
  margin-right: auto;
  padding-bottom: 20px;
  font-size: 18px;
}
.href-button {
  display: flex;
  height: auto;
  justify-content: center;
  min-width: 100%;
}
.img {
  margin-top: 20px;
  margin-bottom: 20px;
  width: 90%;
}
.Android {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.iPhone {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>