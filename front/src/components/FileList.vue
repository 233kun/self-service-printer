<script setup>
import {IconFileTypeDocx, IconBackspace, IconFileTypeDoc, IconFileTypePdf} from '@tabler/icons-vue';
import axios from "axios";
import config from "@/assets/config.js";
import {useMessage} from 'naive-ui'
import {ElMessage} from 'element-plus'
import {onBeforeMount, onBeforeUnmount, onMounted, onUnmounted, onUpdated, reactive, ref, toRef, watch} from "vue";

const props = defineProps({
  fileList: null
})
// const props = reactive({
//   fileList: [
//     {
//       id: 0,
//       name: "test.docx",
//       status: "finished"
//     },
//     {
//       id: 0,
//       name: "test.docx",
//       status: "finished"
//     }
//   ]
// })
const data = ref({
  copies: 1,
  startPage: 1,
  endPage: 1,
  isDoubleSide: false,
  loading: true,
  isConvertFinished: false
})
const change = () => {
  console.log(props.fileList)
}
onUpdated(() => {
    console.log(11)

})
// watch(props.fileList, (newX) => {
//   console.log(newX)
//   // console.log(1)
//   // clearInterval(interval);
//   // setInterval(() => {
//   //   getConvertStatus()
//   // }, 5000)
// }, { deep: true })
const toRefStrHtml = toRef(props, "fileList");

watch(toRefStrHtml, () => {
  // ......
  // if (toRefStrHtml === null)
  console.log(toRefStrHtml.value)
  console.log(22)
},{deep: true , immediate: false})
const getConvertStatus = () => {
  axios.post(config.baseURL + "/convert/status/", {
    "files": files
  }, {
    'Accept': 'application/json',
    "Authentication": window.localStorage.getItem("token")
  }).then((res) => {
    if (res.data.message === "processing") {
      data.isConvertFinished = true
      return
    }
    if (res.data.message === "success") {
      data.isConvertFinished = false
      return
    }
  })
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
      <li v-for="(item, index) in props.fileList" :key="item">
        <div class="test" v-loading="data.isConvertFinished">
          <div class="upload-file-info">
            <div class="icon-and-filename">
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
          <div class="print-info">
            <div class="print-copies">
              <a>打印份数</a>
              <el-input-number v-model="num" :min="1" :max="10" @change="handleChange"/>
            </div>
            <div class="print-range">
              <a>打印范围</a>
              <div class="input-form-wrapper">
                <el-input class="input-form" v-model="data.startPage"/>
                <a class="slash"> / </a>
                <el-input class="input-form" v-model="data.endPage"/>
              </div>
            </div>
            <div class="print-side">
              <a>双面打印</a>
              <div>
                <a>单面</a>
                <el-switch v-model="data.isDoubleSide"
                           style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949">
                </el-switch>
                <a>双面</a>
              </div>
            </div>
          </div>
        </div>
      </li>
    </TransitionGroup>
  </div>
</template>


<style scoped>
.file-name {
  padding: 8px;
}

.icon-and-filename {
  display: flex;
  align-items: center;
}

.test {
  background: #FFFFFF;
  margin-top: 20px;
  padding: 8px;
  border-radius: 12px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, .14);
}

.upload-file-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  animation: fade 2s linear 0s infinite;
}

.upload-file-list {
  list-style: none;
  width: 90%;
  padding: 0px;
  margin: auto;
}


.print-copies {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}

.print-range {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}

.print-side {
  height: 44px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.wrapper {
}

.input-form {
  width: 50px;
}

.slash {
  font-size: 20px;
}

.input-form-wrapper {
  display: flex;
  flex-direction: row;

}

.wrapper {
}

.el-loading-mask {
  z-index: 9;
  border-radius: 12px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, .14);
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