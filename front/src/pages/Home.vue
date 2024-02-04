<script setup>
import {onMounted, onUnmounted, reactive, ref} from "vue";
import config from "@/assets/config.js";
import axios from "axios";
import FileList from "@/components/FileList.vue";
import {ElMessage, ElNotification} from 'element-plus'

const data = reactive(
    {
      inputFile: null,
      files: null,
      fileList: []
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
    const uploadFile = new FormData();
    uploadFile.append("file", data.files[i]);
    axios.put(config.baseURL + "/uploadfile", uploadFile, {
      headers: {
        'Accept': 'application/json',
        'Content-Type': "multipart/form-data",
        'Authentication': window.localStorage.getItem("token")
      }
    }).then(
        res => {
          console.log(res)
          data.fileList.push(
            {
              id: i,
              name: data.files[i - 1].name,
              status: "finished"
            }
          )
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
  <div>
    <div class="uploader">
      <n-button type="primary" class="upload-button" @click="chooseFile()">
        <input type="file" multiple id="input-file" v-show="false" @change="inputFileChange">
        <a class="button-text">点击上传文件</a>
      </n-button>
    </div>
    <FileList :fileList="data.fileList"></FileList>
  </div>
</template>
<style scoed>
.uploader {
  display: flex;
  width: 100%;
  height: 80px;
  justify-content: center
}

.upload-button {
  width: 330px;
  height: 100%;
  border-radius: 12px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, .14);
  margin-right: auto;
  margin-left: auto;
}

.button-text {
  color: white;
  font-size: 24px;
}

</style>
