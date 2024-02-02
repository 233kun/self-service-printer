<script setup>
  import { IconFileTypeDocx, IconBackspace, IconFileTypeDoc , IconFileTypePdf} from '@tabler/icons-vue';
  const props = defineProps({
  fileList: {
    type: Object
  }
})
  const deleteFile = {

  }
</script>

<template>
<!--  <TransitionGroup name="list" tag="ul">-->
<!--  <div class="upload-file-list" v-for="item in valueData">-->
<!--    <ul class="upload-file-info">-->
<!--      <icon-file-type-docx></icon-file-type-docx>-->
<!--      <span class="file-name">{{item.name}}</span>-->
<!--    </ul>-->
<!--  </div>-->
<!--  </TransitionGroup>-->
  <div class="wrapper">
  <TransitionGroup name="list" tag="ul" class="upload-file-list">
  <li v-for="item in fileList" :key="item">
    <div class="upload-file-info">
      <div>
        <icon-file-type-docx v-if="item.name.split('.')[item.name.split('.').length - 1] === 'docx'"></icon-file-type-docx>
        <IconFileTypeDoc v-else-if="item.name.split('.')[item.name.split('.').length - 1] === 'doc'"></IconFileTypeDoc>
        <IconFileTypePdf v-else></IconFileTypePdf>

<!--        狗屎代码，要重写-->
        <span class="file-name">{{item.name}}</span>
      </div>
      <IconBackspace @click="console.log(item.name)"></IconBackspace>
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
    padding:0; margin:0;
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