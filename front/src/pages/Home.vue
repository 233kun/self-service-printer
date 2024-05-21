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

async function getToken() {
  let token = ref()
  await axios.get(config.baseURL + "/token/generation").then(
      res => {
        token = res.data.data.token
      }
  )
  return token
}

const renewToken = async (oldToken) => {
  let token
   await axios.post(config.baseURL + "/token/renew", {
    "token": oldToken
  }).then(res => {
    token = res.data.data.token
   })
  return token
}

const checkToken = () => {
  if (window.localStorage.getItem("token") == null) {
    getToken().then(
        res => {
          window.localStorage.setItem("token", res)
        }
    )
    window.localStorage.setItem("token", getToken())
  } else {
    renewToken(window.localStorage.getItem("token")).then(
        res => {
           window.localStorage.setItem("token", res)
          getFileList(window.localStorage.getItem("token"))
        }
    )
  }
}

let inputImage = reactive()
let inputFile = reactive()

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
  inputFile.click()
}
const chooseImage = () => {
  inputImage.click()
}

const inputFileChange = () => {
  const uploadFile = new FormData()
  // uploadFile is used to store files data
  // fileList is used to store files information
  // data.files = data.inputFile.files
  for (let length = inputFile.files.length, i = 0; i < length; i++) {
    uploadFile.append("files",  inputFile.files[i])
    fileList.value[inputFile.files[i].name] = {
      "filename":  inputFile.files[i].name,
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

onMounted(async () => {
  document.title = "30栋304打印店"
  inputFile = reactive(
      document.getElementById("input-file")
  )
  inputImage = reactive(
      document.getElementById("input-image")
  )
  checkToken()
})
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
