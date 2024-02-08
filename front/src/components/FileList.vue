<script setup>
import {IconFileTypeDocx, IconBackspace, IconFileTypeDoc, IconFileTypePdf} from '@tabler/icons-vue';
import axios from "axios";
import config from "@/assets/config.js";
import {useMessage} from 'naive-ui'
import {ElMessage} from 'element-plus'
import {onBeforeMount, onBeforeUnmount, onMounted, onUnmounted, reactive, ref, watch} from "vue";

const props = defineProps({
  fileList: {
    type: Object
  }
})
watch() => {}
const getConvertStatus = (number) => {
  // for (let file in props.fileList) {
  //   console.log(1)
  //   files.push(file.name)
  // }
  // console.log(files)
  // axios.post(config.baseURL + "/convert/status/" , {
  // "files": files
  // },{
  //   'Accept': 'application/json',
  //     "Authentication": window.localStorage.getItem("token")
  // })
}
const removeFile = (filename, index) => {
  axios.post(config.baseURL + "/uploadfile/remove", {
    "filename": filename
  }, {
    headers: {
      'Accept': 'application/json',
      "Authentication": window.localStorage.getItem("token")
    }
  }).then(res => {
    if (res.data.message === "success") {
      props.fileList.splice(index, 1)
    }
  }).catch(error => {
        ElMessage.error("删除失败")
      }
  )
}
</script>

<template>
  <div class="wrapper">
    <TransitionGroup name="list" tag="ul" class="upload-file-list">
      <li v-for="(item, index) in fileList" :key="item">
        <div class="upload-file-info">
          <div>
            <icon-file-type-docx
                v-if="item.name.split('.')[item.name.split('.').length - 1] === 'docx'"></icon-file-type-docx>
            <IconFileTypeDoc
                v-else-if="item.name.split('.')[item.name.split('.').length - 1] === 'doc'"></IconFileTypeDoc>
            <IconFileTypePdf v-else></IconFileTypePdf>
            <!--        狗屎代码，要重写-->
            <span class="file-name">{{ item.name }}</span>
          </div>
          <IconBackspace @click="removeFile(item.name, index)"></IconBackspace>
        </div>
      </li>
    </TransitionGroup>
  </div>
</template>


<style scoped>
.file-name {
  padding: 8px;
}

.upload-file-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 0;
  animation: fade 2s linear 0s infinite;
}

.upload-file-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.upload-file-list {
  padding: 6px;
}

.wrapper {
  margin: 6px;
}

.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>