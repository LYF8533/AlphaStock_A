<template>
  <div>
    <div style="padding: 10px; border-bottom: 1px solid #ccc;">
      <button @click="currentPage = 'select'" :style="{ fontWeight: currentPage === 'select' ? 'bold' : 'normal' }">选股</button>
      <button @click="currentPage = 'backtest'" :style="{ fontWeight: currentPage === 'backtest' ? 'bold' : 'normal' }"
              style="margin-left: 10px;">回测
      </button>
    </div>
    <SelectPage v-if="currentPage === 'select'"/>
    <Backtest v-else/>
  </div>
</template>

<script setup>
import {ref} from 'vue'
import SelectPage from './components/SelectPage.vue'
import Backtest from './components/Backtest.vue'

const currentPage = ref('select')  // 默认显示选股页面
</script>