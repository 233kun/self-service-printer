<script setup>
import {computed, reactive, ref} from "vue";
import { Decimal } from 'decimal.js'

const props = defineProps({
  fileList: {
    type: Object
  }
})


const rawPrice = computed({
  // getter
  get() {
    let price = new Decimal(0)
    for (let file in props.fileList) {
      let startPage = new Decimal(parseInt(props.fileList[file].print_range_start))
      let endPage = new Decimal(parseInt(props.fileList[file].print_range_end))
      let pageNumber = endPage.sub(startPage).plus(1)
      // price = startPage.add(endPage)
      // price = Decimal.add(Decimal.mul(Decimal.add(Decimal.sub(endPage, startPage), 1), window.config.price), price).mul(props.fileList[file].print_copies)
      price = pageNumber.mul(window.config.price).mul(props.fileList[file].print_copies).add(price)
    }
    return price
  }
})
const discountedPrice = computed({
  get() {
    let price = new Decimal(0)
    for (let file in props.fileList) {
      let startPage = new Decimal(parseInt(props.fileList[file].print_range_start))
      let endPage = new Decimal(parseInt(props.fileList[file].print_range_end))
      let pageNumber = endPage.sub(startPage).plus(1)
      if (props.fileList[file].print_side === "one-sided") {
         price = pageNumber.mul(window.config.price).mul(props.fileList[file].print_copies).add(price)
        console.log(price.toNumber())
        continue
      }
      if (pageNumber % 2 === 0) {
        price = pageNumber.mul(window.config.discountedPrice).mul(props.fileList[file].print_copies).add(price)
      } else {
        price = pageNumber.sub(1).mul(window.config.discountedPrice).add(window.config.price).mul(props.fileList[file].print_copies).add(price)
      }
    }
    return price
  }
})

// fullname.value = ref(props.fileList)

</script>

<template>
  <div class="wrapper">
    <a>原价：    {{rawPrice}}</a>
<!--    <a>优惠：    {{rawPrice - discountedPrice}}</a>-->
    <a>实付：    {{discountedPrice}}</a>
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
  background-color: white;
  font-size: 20px;

}

</style>