<script setup>
import {onMounted, onUnmounted, reactive, ref} from "vue";
  import config from "@/assets/config.js";
  import axios from "axios";
  import FileList from "@/components/FileList.vue";
  const data = reactive(
      {
        inputFile: null,
        files: null,
        filesList: []
      }
  )
  const checkToken = () => {
    if (window.localStorage.getItem("token") == null) {
          axios.get(config.baseURL + "/token/get")
              .then(res => {
                window.localStorage.setItem("token", res.data.token)
              })
      return
    }
    axios.post(config.baseURL + "/token/renew", {
      "token": window.localStorage.getItem("token")
    },{
    }).then(res => {
      window.localStorage.setItem("token", res.data.token)
    })
    ///////////////////////////////////////////////////////////////////////
    //  获取已保存的文件，放在此是可以让第一次进入网站的用户不用获取                //
    ///////////////////////////////////////////////////////////////////////
    getFileList()
  }
  onMounted(()=>{
    data.inputFile = reactive(
    document.getElementById("input-file")
    )
    checkToken()
    // data.filesList.push(getFileList()
    // console.log(data.filesList)
    // console.log(getFileList())
  })
onUnmounted(()=> {
  console.log(getFileList().value)
        // data.filesList.push(getFileList())
})
  //     const testButton = () => {
  //   const uploaddata = new FormData();
  // uploaddata.append("file", data.files[0]);
  //   console.log(data.files[0].name)
  //     axios.post("http://localhost:8000/uploadfile", uploaddata, {
  //       headers: {'Accept': 'application/json',
  //                                          "Content-Type": "multipart/form-data",        }
  //     })
  //   }

  const getFileList = () => {
    axios.get(config.baseURL + "/uploadfile/filelist", {
      headers: {
        "Authentication": window.localStorage.getItem("token")
      }
    }).then(res => {
          if (res.data.message === "fail") {
            return null
          }
      console.log(res)
          const fileList = [];
          for (var i = 0; i < res.data.message.length; i++) {
            fileList[i] = {
              id: i,
              name: res.data.message[i],
              status: "finished"
            }
          data.filesList = data.filesList.concat(fileList)
          }
      })
  }
  const chooseFile = () => {
    data.inputFile.click()
  }
  const inputFileChange = () => {
    data.files = data.inputFile.files
    for (var length = data.files.length ,i = 0; i < length; i++) {
       data.filesList.push( {
         id: i,
         name: data.files[i].name,
         status: "finished"
       }
    )
     }
    for (var length = data.files.length ,i = 0; i < length; i++) {
      const uploadFile = new FormData();
      uploadFile.append("file", data.files[i]);
      axios.post(config.baseURL + "/uploadfile/" + window.localStorage.getItem("token"),uploadFile , {
        'Accept': 'application/json',
        'Content-Type': "multipart/form-data",
    })
    }
  }
</script>

<template>
  <div>
    <div class="uploader" >
      <n-button type="primary" class="upload-button" @click="chooseFile()">
        <input type="file" multiple id="input-file" v-show="false" @change="inputFileChange">
        <a class="button-text">点击上传文件</a>
      </n-button>
    </div>
<!--          <n-upload-->
<!--          show-preview-button-->
<!--          :default-file-list="data.filesList"-->
<!--          show-remove-button = "True"-->
<!--          list-type="image"-->
<!--      >-->
<!--      </n-upload>-->
    <FileList :fileList="data.filesList"></FileList>
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
    box-shadow: 0 3px 6px rgba(0,0,0,.14);
    margin-right: auto;
    margin-left: auto;
  }
  .button-text {
    color: white;
    font-size: 24px;
  }

</style>
