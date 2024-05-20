<script setup>
import {onMounted, onUnmounted, reactive, ref} from "vue";
// import config from "@/assets/config.js";
import config from "@/assets/config.js";
import axios from "axios";
import FileList from "@/components/FileList.vue";
import {ElMessage, ElNotification} from 'element-plus'
import PayButton from "@/components/PayButton.vue";
import PriceCounter from "@/components/PriceCounter.vue";
import {IconFiles, IconPhoto, IconBook, IconBrandAndroid} from '@tabler/icons-vue';

const data = reactive(
    {
      inputFile: null,
      files: null,
    }
)

async function getToken() {
  let token = ""
  token = await axios.get(config.baseURL + "/token/get")
  return token
}

async function renewToken() {
  let token = ""
  token = axios.post(config.baseURL + "/token/renew", {
    "token": window.localStorage.getItem("token")
  })
  return token
}

const checkToken = () => {
  if (window.localStorage.getItem("token") == null) {
    getToken().then(async (res) => {
      window.localStorage.setItem("token", res.data.token)
      getFileList(res.data.token)
    })
  } else {
    renewToken().then((res) => {
      console.log(res.data.token)
      window.localStorage.setItem("token", res.data.token)
      getFileList(res.data.token)
    })
  }
}

let inputImage = reactive()

onMounted(async () => {
  console.log(config.baseURL)
  document.title = "30栋304打印店"
  data.inputFile = reactive(
      document.getElementById("input-file")
  )
  inputImage = reactive(
      document.getElementById("input-image")
  )
  await checkToken()
})

const fileList = reactive({})
const isShowPayArea = ref(false)
const getFileList = (token) => {
  let isConvertFinished = true
  axios.get(config.baseURL + "/uploadfile/filelist", {
    headers: {
      "Authentication": token
      // "Authentication": getToken()
    }
  }).then(res => {
    if (res.data.message === "fail") {
      return
    }
    fileList.value = res.data.data
    for (let item in res.data.data) {
      if (item.convert_stata === "processing") {
        isConvertFinished = false
        break
      }
      if (item.convert_stata === "error") {
        isConvertFinished = false
      }
    }
    if (isConvertFinished === true) {
      if (JSON.stringify(res.data.data) !== "{}") {
        isShowPayArea.value = true;
      }
    }
    return "none"
  }).catch(
      error => {
        console.log(error)
        ElMessage.error("初始化失败：error code 3")
      }
  )
  return null
}


const chooseFile = () => {
  data.inputFile.click()
}
const chooseImage = () => {
  inputImage.click()
}

const inputFileChange = () => {
  const uploadFile = new FormData()
  // uploadFile is used to store files data
  // fileList is used to store files information
  data.files = data.inputFile.files
  for (let length = data.files.length, i = 0; i < length; i++) {
    uploadFile.append("files", data.files[i])
    fileList.value[data.files[i].name] = {
      "filename": data.files[i].name,
      "convert_state": "processing",
    }
  }
  console.log(fileList)
  for (let length = inputImage.files.length, i = 0; i < length; i++) {
    uploadFile.append("files", inputImage.files[i])
    fileList[inputImage.files[i].name] = {
      "filename": inputImage.files[i].name,
      "convert_state": "processing",
    }
  }
  axios.put(config.baseURL + "/uploadfile", uploadFile, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': "multipart/form-data",
      'Authentication': window.localStorage.getItem("token")
    }
  }).then(
      res => {
        getFileList(window.localStorage.getItem("token"))
      }
  ).then((error) => {
    console.log(error)
  })
}
const herfToAndroidPayTutorial = () => {
      window.location.href = "https://233kun.top"
}
</script>

<template>
  <div class="wrapper">
    <div>
      <div class="uploader-wrapper">
        <n-button type="primary" class="upload-button" @click="chooseFile()">
          <input type="file" multiple id="input-file" accept=".doc, .docx, .xlsx, .xls, .pdf" v-show="false"
                 @change="inputFileChange">
          <div class="button-image-and-font">:
            <IconFiles/>
            <a class="button-text">打印文档</a></div>
        </n-button>
        <div class="upload-button-wrapper">
          <n-button color="#5B5B5B" class="upload-image-button" @click="chooseImage()">
            <input type="file" multiple id="input-image" accept=".jpg" v-show="false" @change="inputFileChange">
            <div class="button-image-and-font">
              <IconPhoto/>
              <a class="button-text">打印图片</a></div>
          </n-button>
          <n-button type="info" class="upload-image-button">
            <div class="button-image-and-font">
              <IconBook/>
              <a class="button-text">使用教程</a></div>
          </n-button>
        </div>
        <n-button strong secondary type="primary" class="android-pay-tutorial-button">
          <input type="file" multiple id="input-file" accept=".doc, .docx, .xlsx,.pdf" v-show="false"
                 @change="inputFileChange">
          <div class="button-image-and-font" @click="herfToAndroidPayTutorial()">
            <IconBrandAndroid/>
            <a class="button-text" style="color: #18a058">安卓无法支付点这</a></div>
        </n-button>
      </div>
      <div class="filelist-wrapper">
        <FileList :fileList="fileList.value" class="field-list"></FileList>
      </div>
    </div>
    <div v-if="isShowPayArea" class="pay-area">
      <div class="price-counter">
        <PriceCounter :fileList="fileList.value"></PriceCounter>
      </div>
      <div class="pay-bottom">
        <pay-button :fileList="fileList.value"></pay-button>
      </div>
    </div>
  </div>
</template>
<style scoed>
html, body, #app {
  background-color: #F2F2F2;
  margin: 0;
  padding: 0;
  height: 100%;
}

.wrapper {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}

.uploader-wrapper {
  display: flex;
  flex-direction: column;
  height: auto;
  align-items: center;
  width: 100%;
}

.upload-button-wrapper {
  width: 90%;
  display: flex;
  justify-content: space-between;
}

.upload-button {
  width: 90%;
  padding-top: 15%;
  padding-bottom: 15%;
  border-radius: 12px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, .14);
  margin-top: 20px;
}

.upload-image-button {
  width: 45%;
  padding-top: 10%;
  padding-bottom: 10%;
  border-radius: 12px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, .14);
  margin-top: 20px;
}
.android-pay-tutorial-button {
  width: 90%;
  padding-top: 10%;
  padding-bottom: 10%;
  border-radius: 12px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, .14);
  margin-top: 20px;
}
.button-image-and-font {
  display: flex;
  align-items: center;
}

.button-text {
  color: white;
  font-size: 24px;
}

.field-list {
}

.filelist-wrapper {
  width: 100%;
}

.pay-area {
  width: 90%;
  display: flex;
  justify-content: space-between;
  margin-left: auto;
  margin-right: auto;
  margin-top: 10%;
  padding-bottom: 10%;
}

.price-counter {
  width: 150px;
  height: 150px;
  border-radius: 12px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, .14);
}

.pay-bottom {
  width: 150px;
  height: 150px;
  border-radius: 12px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, .14);
}
</style>
