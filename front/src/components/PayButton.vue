<script setup>
import { IconBrandAlipay } from '@tabler/icons-vue';
import axios from "axios";
import config from "@/assets/config.js";
import {ref} from "vue";
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
  axios.post(config.baseURL + "/pay/bill/create", {
    "fileList": props.fileList
  }, {
    headers: {
              'Accept': 'application/json',
        "Content-Type": "application/json",
      'Authentication': window.localStorage.getItem("token")
    }
  }).then(res => {
    payLink = res.data.message
    window.location.href = res.data.message
    // window.open(res.data.message)
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