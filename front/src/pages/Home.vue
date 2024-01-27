<script setup>
  import {onMounted, reactive, ref} from "vue";
  const data = reactive(
      {
        inputFile: null,
        files: null,
        filesList: []
      }
  )
  onMounted(()=>{
    data.inputFile = reactive(
    document.getElementById("input-file")
    )
  })
  const chooseFile = () => {
    data.inputFile.click()
  }
  const inputFileChange = () => {
    data.files = data.inputFile.files
    for (var length = data.files.length ,i = 0; i < length; i++) {
       data.filesList[i] = {
         id: i,
         name: data.files[i].name,
         status: "finished"
       }
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
      <n-upload
          show-preview-button
          :default-file-list="data.filesList"
          list-type="image"
      >
      </n-upload>
    </div>
  </div>
</template>
<style scoed>
  .uploader {
    width: 330px;
    height: 80px;
  }
  .upload-button {
    width: 100%;
    height: 100%;
    border-radius: 12px;
    box-shadow: 0 3px 6px rgba(0,0,0,.14);
  }
  .button-text {
    color: white;
    font-size: 24px;
  }

</style>
