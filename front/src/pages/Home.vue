<script setup>
import {onMounted, onUnmounted, reactive, ref, watch, defineExpose} from "vue";
import axios from "axios";
import FileList from "@/components/FileList.vue";
import {ElMessage, ElNotification} from 'element-plus'
import PayButton from "@/components/PayButton.vue";
import PriceCounter from "@/components/PriceCounter.vue";
import {IconFiles, IconPhoto, IconBook, IconBrandAndroid} from '@tabler/icons-vue';

// ** deprecated **

// async function getToken() {
//   let token
//   await axios.get(window.config.baseURL + "/token/generation").then(
//       res => {
//         token = res.data.data.token
//       }
//   )
//   return token
// }
// const renewToken = async (oldToken) => {
//   let token
//   await axios.post(window.config.baseURL + "/token/renew", {
//     "token": oldToken
//   }).then(res => {
//     token = res.data.data.token
//   })
//   return token
// }

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
          setFileList(window.localStorage.getItem("token"))
        }
    )
  }
}
const getFilesAttributes = async (token) => {
  let authentication
  if (token === null) {
    authentication = 'none';
  } else {
    authentication = token
  }
  let files_attributes;
  await axios.get(window.config.baseURL + "/uploadfile/filelist", {
    headers: {
      "Authentication": authentication
    }
  }).then(res => {
    if (res.data.message !== 'success') {
      ElMessage.error(res.data.message);
    } else {
      files_attributes = res.data.data.files_attributes
      localStorage.setItem('token', res.data.data.token) // set token
    }
  }).catch(err => {
        console.log(err)
        ElMessage.error('请求服务器失败');
      }
  )
  return files_attributes
};
const lPollConvertStatus = async (token) => { //long polling
  let message
  await axios.get(window.config.baseURL + '/uploadfile/convert_status', {
    headers: {
      "Authentication": token
    }
  }).then(res => {
    message = res.data.message
  })
  return message
}
const fileList = reactive([])
// const fileList_testing_env = ref('[ { "print_copies": 1, "print_range_start": 1, "print_side": "one-sided", "filename": "实验二 盒子模型的应用.pdf", "convert_state": "success", "print_range_end": 1 }, { "print_copies": 1, "print_range_start": 1, "print_side": "one-sided", "filename": "实验二 盒子模型的应用.pdf", "convert_state": "success", "print_range_end": 1 }, { "print_copies": 1, "print_range_start": 1, "print_side": "one-sided", "filename": "实验二 盒子模型的应用.pdf", "convert_state": "success", "print_range_end": 1 }, { "print_copies": 1, "print_range_start": 1, "print_side": "one-sided", "filename": "实验二 盒子模型的应用.pdf", "convert_state": "success", "print_range_end": 1 } ] ')
const setFileList = async (token) => {
  await getFilesAttributes(token).then(res => {
    fileList.value = res
  })
  for (let file of fileList.value) {
    if (file.convert_state === 'processing' || file.convert_state === 'pending') {
      lPollConvertStatus(token).then(res => {
        if (res === 'success') {
          setFileList(token)
        }
      })
    }
  }
}
const chooseFile = () => {
  inputFiles.click()
}
const chooseImage = () => {
  inputImages.click()
}
let inputImages = reactive()
let inputFiles = reactive()
const handleFormFilesInput = () => { //handleFileUpload
  let uploadFiles = new FormData()
  for (let length = inputFiles.files.length, i = 0; i < length; i++) {
    uploadFiles.append("files", inputFiles.files[i])
    fileList.value.push({
      "filename": inputFiles.files[i].name,
      "convert_state": "processing",
      "total_pages": '1'
    })
  }
  for (let length = inputImages.files.length, i = 0; i < length; i++) {
    uploadFiles.append("files", inputImages.files[i])
    fileList.value.push({
      "filename": inputImages.files[i].name,
      "convert_state": "processing",
      "total_pages": '1'
    })
  }
  axios.put(window.config.baseURL + "/uploadfile", uploadFiles, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': "multipart/form-data",
      'Authentication': window.localStorage.getItem("token")
    }
  }).then(
      res => {
        inputImages.value = ''
        inputFiles.value = ''
        setFileList(window.localStorage.getItem("token"))
      }
  ).then((error) => {
    console.log(error)
  })
}
const hrefTutorial = () => {
  const ua = navigator.userAgent
  if (ua.includes('iphone')) {
    window.open('/public/static/tutorial/ios-tutorial.html')
  } else
    window.open('/public/static/tutorial/android-tutorial.html')
}
onMounted(async () => {
  // console.log(window.config.test)
  await setFileList(window.localStorage.getItem("token"))
  // document.title = "30栋304打印店"
  inputFiles = reactive(
      document.getElementById("input-files")
  )
  inputImages = reactive(
      document.getElementById("input-image")
  )
})
const isShowPayArea = ref(false)
watch(() => fileList.value,  () => {
  for (let file of fileList.value) {
    if (file.convert_state === 'processing' || file.convert_state === 'pending') {
      break
    } else {
      isShowPayArea.value = true
    }
  }
}, {deep: true})
</script>

<template>
  <div class="wrapper">
    <div>
      <div class="uploader-wrapper">
        <n-button type="primary" class="upload-button" @click="chooseFile()">
          <input type="file" multiple id="input-files" accept=".doc, .docx, .xlsx, .xls, .pdf" v-show="false"
                 @change="handleFormFilesInput">
          <div class="button-image-and-font">:
            <IconFiles/>
            <a class="button-text">打印文档</a></div>
        </n-button>
        <div class="upload-button-wrapper">
          <n-button color="#5B5B5B" class="upload-image-button" @click="chooseImage()">
            <input type="file" multiple id="input-image" accept=".jpg" v-show="false" @change="handleFormFilesInput">
            <div class="button-image-and-font">
              <IconPhoto/>
              <a class="button-text">打印图片</a></div>
          </n-button>
          <n-button type="info" class="upload-image-button" @click="hrefTutorial()">
            <div class="button-image-and-font">
              <IconBook/>
              <a class="button-text">使用教程</a></div>
          </n-button>
        </div>
<!--        <n-button strong secondary type="primary" class="android-pay-tutorial-button">-->
<!--          <input type="file" multiple id="input-file" accept=".doc, .docx, .xlsx,.pdf" v-show="false"-->
<!--                 @change="handleFormFilesInput">-->
<!--          <div class="button-image-and-font" @click="herfToAndroidPayTutorial()">-->
<!--            <IconBrandAndroid/>-->
<!--            <a class="button-text" style="color: #18a058">安卓无法支付点这</a></div>-->
<!--        </n-button>-->
      </div>
      <div class="filelist-wrapper">
        <FileList :fileList="fileList" :getFilesAttributes="getFilesAttributes" class="field-list"></FileList>
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
