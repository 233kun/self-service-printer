<script setup>
import {
  IconFileTypeDocx,
  IconBackspace,
  IconFileTypeDoc,
  IconFileTypePdf,
  IconFileTypeXls,
  IconAlertCircleFilled,
  IconPhoto,
  IconMinus
} from '@tabler/icons-vue';
import axios from "axios";
import {useMessage} from 'naive-ui'
import {ElMessage} from 'element-plus'
import {onBeforeMount, onBeforeUnmount, onMounted, onUnmounted, onUpdated, reactive, ref, toRef, watch} from "vue";
import getFilesAttributes from '../pages/Home.vue'
const props = defineProps({
  fileList: {
    type: Object
  },
  getFilesAttributes: {
    type: Object
  }
})
const data = ref({
  copies: 1,
  startPage: "",
  endPage: "",
  isDoubleSide: false,
  loading: true,
  isConvertFinished: false
})
const sideOption = [
  {
    value: 'one-sided',
    label: '单面',
  },
  {
    value: 'two-sided-default',
    label: '双面(默认)',
  },
  {
    value: 'two-sided-long-edge',
    label: '双面(长边翻页)',
  },
  {
    value: 'two-sided-short-edge',
    label: '双面(短边翻页)',
  }
]
const value = ref('')
const removeFile = (filename, index) => {
  axios.post(window.config.baseURL + "/uploadfile/remove", {
    "filename": filename
  }, {
    headers: {
      'Accept': 'application/json',
      'Authorization': 'Bearer ' + window.localStorage.getItem("token")
    }
  }).then(res => {
    if (res.data.message === "success") {
      console.log(props.getFilesAttributes(window.localStorage.getItem("token")))
      props.getFilesAttributes(window.localStorage.getItem("token")).then(res => {
        props.fileList.value = res
      })
      props.fileList.value = []
    }
  }).catch(error => {
        ElMessage.error("删除失败")
        console.log(error)
      }
  )
}
const handleConvertState = (state) => {
  if (state === "success") {
    return false
  }
  if (state === "processing") {
    return true
  }
  return true
}
const preview = (filename) => {
  window.open('/pdfjs/web/viewer.html?file=' + window.config.baseURL + `/preview/${window.localStorage.getItem("token")}/${filename}`)
}

</script>

<template>
  <div class="filelist">
    <TransitionGroup name="list" tag="ul" class="upload-file-list">
      <li v-for="(item, index) in props.fileList.value" :key="item">
        <div class="wrapper">
          <div class="upload-file-info">
            <div class="head-warpper">
              <div class="icon-and-filename">
                <icon-file-type-docx class="icon"
                                     v-if="item.filename.split('.')[item.filename.split('.').length - 1] === 'docx'"></icon-file-type-docx>
                <IconFileTypeDoc class="icon"
                                 v-else-if="item.filename.split('.')[item.filename.split('.').length - 1] === 'doc'"></IconFileTypeDoc>
                <IconFileTypeXls class="icon"
                                 v-else-if="item.filename.split('.')[item.filename.split('.').length - 1] === 'xls'"></IconFileTypeXls>
                <IconFileTypeXls class="icon"
                                 v-else-if="item.filename.split('.')[item.filename.split('.').length - 1] === 'xlsx'"></IconFileTypeXls>
                <IconFileTypePdf class="icon"
                                 v-else-if="item.filename.split('.')[item.filename.split('.').length - 1] === 'pdf'"></IconFileTypePdf>
                <IconPhoto class="icon"
                           v-else-if="item.filename.split('.')[item.filename.split('.').length - 1] === 'jpg'"></IconPhoto>
                <IconPhoto class="icon"
                           v-else-if="item.filename.split('.')[item.filename.split('.').length - 1] === 'jpeg'"></IconPhoto>
                <IconPhoto class="icon"
                           v-else-if="item.filename.split('.')[item.filename.split('.').length - 1] === 'png'"></IconPhoto>

                <div class="file-name">
                  <a>{{ item.filename }}</a>
                </div>
              </div>
              <IconBackspace class="icon" @click="removeFile(item.filename)"></IconBackspace>
            </div>
          </div>
          <div class="print-info" :style="item.convert_state==='success'?'display: unset':'display: none'">
            <!--          <div class="print-info" style="visibility: hidden;>-->
            <div class="print-copies">
              <a> 打印份数</a>
              <el-input-number v-model="item.print_copies" :min="1"/>
            </div>
            <div class="print-range">
              <a>打印范围</a>
              <div class="input-form-wrapper">
                <el-input class="input-form" v-model="item.print_range_start" :placeholder="1"/>
                <a class="slash">  </a>
                <IconMinus/>
                <el-input class="input-form" v-model="item.print_range_end" :placeholder="item.total_pages"/>
<!--                type error-->
              </div>
            </div>
            <div class="print-side">
              <a>双面打印</a>
              <div>
                <el-select
                    class="selector"
                    v-model="item.print_side"
                    placeholder="Select"
                    size="large"
                >
                  <el-option
                      v-for="item in sideOption"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                  />
<!--                                      default-first-option="one-sided"-->

                </el-select>
              </div>
            </div>
            <div class="preview">
              <div>
                预览文件
              </div>
              <n-button type="warning" @click="preview(item.filename)">
                预览
              </n-button>
            </div>
          </div>
          <div class="processing" v-if="item.convert_state === 'processing'">
            <div class="loading"></div>
          </div>
          <div class="warning" v-if="item.convert_state === 'error'">
            <div class="warning-text-and-icon"></div>
            <IconAlertCircleFilled class="warning-icon"></IconAlertCircleFilled>
            <a class="warning-text">无法读取文件</a>
          </div>
          <div class="print-info-excel"
               v-if="item.convert_state === 'success' && item.filename.split('.')[item.filename.split('.').length - 1] === 'xlsx' ||
                     item.convert_state === 'success' && item.filename.split('.')[item.filename.split('.').length - 1] === 'xls'">
            <a class="excel-warning-text">Excel表格打印请务必先预览，打印效果可能与实际表格有所不同，建议将表格另存为PDF上传打印</a>
          </div>
        </div>
      </li>
    </TransitionGroup>
  </div>
</template>


<style scoped>

.file-name {
  padding: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.head-warpper {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.icon-and-filename {
  display: flex;
  align-items: center;
  overflow: auto;
}

.icon {
  width: 28px;
  height: 28px;
}

.wrapper {
  background: #FFFFFF;
  margin-top: 20px;
  padding: 8px;
  border-radius: 12px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, .14);
}

.upload-file-info {
  display: flex;
  align-items: center;
  animation: fade 2s linear 0s infinite;
}

.upload-file-list {
  list-style: none;
  width: 90%;
  padding: 0px;
  margin: auto;
}

.print-info {
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
.warning {
  height: 194px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.selector {
  width: 150px;
}
.processing {
  height: 194px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.loading {
  border: 5px solid #e5e5e5;
  border-top: 5px solid rgba(255, 103, 104, 1);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: inline-block;
  animation: turn-around 1.5s linear infinite;
}

@keyframes turn-around {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.preview {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 44px;

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
  align-items: center;
}

.warning-icon {
  width: 64px;
  height: 64px;
  color: #d03050
}

.warning-text {
  font-size: 24px;
}

.wrapper {

}

.excel-warning-icon {
  width: 18px;
  height: 18px;
  color: red;
}

.excel-warning-text {
  color: red;
  display: flex;

}

.excel-waring-wrapper {
  display: flex;
  align-items: center;
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
