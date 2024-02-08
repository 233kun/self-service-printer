<script setup>
  import axios from "axios";
  import {ref} from "vue";
const data = ref({
  copies: 1,
  startPage: 1,
  endPage: 1
})

</script>

<template>
  <div>
    <div>
      <a>打印份数</a>
      <el-input-number v-model="num" :min="1" :max="10" @change="handleChange" />
    </div>
    <div>
      <a>打印范围</a>
      <div>
        <el-input v-model="data.startPage" placeholder="Please input" />
          <el-input v-model="data.endPage" placeholder="Please input" />
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>