<script setup>
import {IconBrandAlipay} from '@tabler/icons-vue';
import axios from "axios";
import {ref} from "vue";
import {ElMessage} from "element-plus";

const props = defineProps({
  fileList: {
    type: Object
  }
})
let payLink = ""
let clickLock = false
const pay = () => {
  if (clickLock === true) {
    window.location.href = payLink
    return
  }
  clickLock = true;
  axios.post(window.config.baseURL + "/pay/bill/create", {
    "fileList": props.fileList
  }, {
    headers: {
      'Accept': 'application/json',
      "Content-Type": "application/json",
      'Authorization': "Bearer " + window.localStorage.getItem("token")
    }
  }).then(res => {
    if (res.data.message !== 'success') {
      ElMessage.error(res.data.message);
    } else {
      payLink = res.data.data.url;
      window.location.href = payLink
    }
  }).catch(err => {
    alert(err)
  });
}
</script>

<template>
  <div class="wrapper" @click="pay">
    <icon-brand-alipay class="icon"></icon-brand-alipay>
  </div>
</template>

<style scoped>
.wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 12px;
  background-color: #1677ff;
}

.icon {
  color: white;
  width: 100px;
  height: 100px;
}
</style>