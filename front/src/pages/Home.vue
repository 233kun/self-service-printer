<script setup>
import {onMounted, onUnmounted, reactive, ref} from "vue";
import config from "@/assets/config.js";
import axios from "axios";
import FileList from "@/components/FileList.vue";
import {ElMessage, ElNotification} from 'element-plus'
import FileInfo from "@/components/FileInfo.vue";

const data = reactive(
    {
      inputFile: null,
      files: null,
      fileList: [],
      isShowFileInfo: false,
    }
)
const checkToken = () => {
  if (window.localStorage.getItem("token") == null) {
    axios.get(config.baseURL + "/token/get")
        .then(res => {
          window.localStorage.setItem("token", res.data.token)
        }).catch(
        error => {
          ElMessage.error("初始化失败：error code 1")
        }
    )
    return
  }
  axios.post(config.baseURL + "/token/renew", {
    "token": window.localStorage.getItem("token")
  }, {}).then(res => {
    window.localStorage.setItem("token", res.data.token)
  }).catch(
      error => {
        ElMessage.error("初始化失败：error code 2")
      }
  )
  ///////////////////////////////////////////////////////////////////////
  //  获取已保存的文件，放在此是可以让第一次进入网站的用户不用获取                //
  ///////////////////////////////////////////////////////////////////////
  getFileList()
}
onMounted(() => {
  data.inputFile = reactive(
      document.getElementById("input-file")
  )
  checkToken()
})

const test = () => {
  axios.post(config.baseURL + "/uploadfile/isFinish", {
    "isFinish": true
  }, {
    headers: {
      'Accept': 'application/json',
      "Content-Type": "application/json",
      'Authentication': window.localStorage.getItem("token")
    }
  })
}
const getFileList = () => {
  axios.get(config.baseURL + "/uploadfile/filelist", {
    headers: {
      "Authentication": window.localStorage.getItem("token")
    }
  }).then(res => {
    if (res.data.message === "fail") {
      return
    }
    const fileList = [];
    for (var i = 0; i < res.data.message.length; i++) {
      fileList[i] = {
        id: i,
        name: res.data.message[i],
        status: "finished"
      }
    }
    data.fileList = data.fileList.concat(fileList)
  }).catch(
      error => {
        ElMessage.error("初始化失败：error code 3")
      }
  )
}
const chooseFile = () => {
  data.inputFile.click()
}
const inputFileChange = () => {
  data.files = data.inputFile.files
  let i = 0
  for (let length = data.files.length; i < length; i++) {
    const uploadFile = new FormData()
    uploadFile.append("file", data.files[i])
    axios.put(config.baseURL + "/uploadfile", uploadFile, {
      headers: {
        'Accept': 'application/json',
        'Content-Type': "multipart/form-data",
        'Authentication': window.localStorage.getItem("token")
      }
    }).then(
        res => {
          data.fileList.push(
              {
                id: i,
                name: data.files[i - 1].name,
                status: "finished"
              }
          )
          axios.post(config.baseURL + "/uploadfile/isFinish", {
            "isFinish": true
          }, {
            headers: {
              'Accept': 'application/json',
              "Content-Type": "application/json",
              'Authentication': window.localStorage.getItem("token")
            }
          })
        }
    ).catch(
        error => {
          ElMessage.error("上传失败")
        }
    )
  }

}
</script>

<template>
  <div class="wrapper">
    <div class="uploader-wrapper">
      <n-button type="primary" class="upload-button" @click="chooseFile()">
        <input type="file" multiple id="input-file" v-show="false" @change="inputFileChange">
        <a class="button-text">点击上传文件</a>
      </n-button>
    </div>
    <div class="filelist-wrapper">
      <FileList :fileList="data.fileList" class="field-list"></FileList>
    </div>
  </div>
</template>
<style scoed>
body {
  background-color: #F2F2F2;
}

.wrapper {
  display: flex;
  flex-direction: column;
}

.uploader-wrapper {
  display: flex;
  height: auto;
  justify-content: center;
}

.upload-button {
  width: 90%;
  padding-top: 15%;
  padding-bottom: 15%;
  border-radius: 12px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, .14);

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
</style>
