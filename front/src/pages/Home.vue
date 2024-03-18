<script setup>
import {onMounted, onUnmounted, reactive, ref} from "vue";
import config from "@/assets/config.js";
import axios from "axios";
import FileList from "@/components/FileList.vue";
import {ElMessage, ElNotification} from 'element-plus'
import PayButton from "@/components/PayButton.vue";
import PriceCounter from "@/components/PriceCounter.vue";

const data = reactive(
    {
      inputFile: null,
      files: null,
      fileList: {},
      isShowFilelist: false,
      isShowPayArea: false
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



onMounted(async () => {
  data.inputFile = reactive(
      document.getElementById("input-file")
  )
  await checkToken()
})
const getFileList = (token) => {
  console.log("test1")
    let isConvertFinished = true
  axios.get(config.baseURL + "/uploadfile/filelist", {
    headers: {
      "Authentication": token
      // "Authentication": getToken()
    }
  }).then(res => {
    console.log(res)
    if (res.data.message === "fail") {
      return
    }
    data.fileList = res.data.message
    console.log(data.fileList)
    console.log(res.data.message)
    data.isShowFilelist = true
    for (let item in res.data.message) {
      if (item.convert_stata === "processing") {
        isConvertFinished = false
        break
      }
      if (item.convert_stata === "error") {
        isConvertFinished = false
      }
    }
    if (isConvertFinished === true) {
      if (JSON.stringify(res.data.message) !== "{}") {
        data.isShowPayArea = true;
      }
    }
    return "none"
  }).catch(
      error => {
        ElMessage.error("初始化失败：error code 3")
      }
  )
  return null
}



const chooseFile = () => {
  data.inputFile.click()
}
const inputFileChange = () => {
    data.files = data.inputFile.files
  const uploadFile = new FormData()
  for (let length = data.files.length, i = 0; i < length; i++) {
    uploadFile.append("files", data.files[i])
          data.fileList[data.files[i].name] = {
          "filename": data.files[i].name,
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
</script>

<template>
  <div class="wrapper">
    <div>
    <div class="uploader-wrapper">
      <n-button type="primary" class="upload-button" @click="chooseFile()">
        <input type="file" multiple id="input-file" accept=".doc, .docx, .pdf" v-show="false" @change="inputFileChange">
        <a class="button-text">点击上传文件</a>
      </n-button>
    </div>
    <div v-if="data.isShowFilelist" class="filelist-wrapper">
      <FileList :fileList="data.fileList" class="field-list"></FileList>
     </div>
      </div>
    <div v-if="data.isShowPayArea" class="pay-area">
      <div class="price-counter">
        <PriceCounter :fileList="data.fileList"></PriceCounter>
      </div>
      <div class="pay-bottom">
        <pay-button :fileList="data.fileList"></pay-button>
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
  height: auto;
  justify-content: center;
  min-width: 100%;
}

.upload-button {
  width: 90%;
  padding-top: 15%;
  padding-bottom: 15%;
  border-radius: 12px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, .14);
  margin-top: 20px;
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
