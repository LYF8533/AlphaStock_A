<template>
  <div style="padding: 20px">
    <h1>沪深300 动量选股</h1>

    <div style="margin: 20px 0;">
      <label>选股参数：</label>
      前 <input v-model.number="topN" type="number" min="1" max="20" style="width:60px"> 只
      <input v-model.number="days" type="number" min="5" max="60" style="width:60px"> 日涨幅
      <button @click="fetchMomentum">选股</button>
    </div>

    <div v-if="topStocks.length">
      <h3>涨幅榜</h3>
      <table border="1" style="width:100%; border-collapse: collapse;">
        <thead>
          <tr>
            <th>代码</th>
            <th>名称</th>
            <th>最新日期</th>
            <th>最新收盘</th>
            <th>{{days}}日前收盘</th>
            <th>涨幅(%)</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in topStocks" :key="s.code">
            <td>{{ s.code }}</td>
            <td>{{ s.name }}</td>
            <td>{{ s.last_date }}</td>
            <td>{{ s.last_close }}</td>
            <td>{{ s.past_close }}</td>
            <td :style="{color: s['gain_'+days+'d'] > 0 ? 'red' : 'green'}">
              {{ s['gain_'+days+'d'] }}%
            </td>
            <td><button @click="selectStock(s.code)">K线</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- K线图区域 -->
    <div v-if="selectedCode" style="margin-top: 30px;">
      <h2>{{ selectedCode }} K线图</h2>
      <StockChart :data="stockHistory" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import StockChart from './StockChart.vue'

const topN = ref(10)
const days = ref(20)
const topStocks = ref([])
const selectedCode = ref('000001')
const stockHistory = ref([])

const fetchMomentum = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/select/momentum', {
      params: { top_n: topN.value, days: days.value }
    })
    topStocks.value = res.data.top
    if (topStocks.value.length) {
      selectStock(topStocks.value[0].code)
    }
  } catch (error) {
    console.error('选股失败', error)
    alert('选股接口调用失败，请检查后端是否运行')
  }
}

const selectStock = async (code) => {
  selectedCode.value = code
  try {
    const res = await axios.get(`http://127.0.0.1:8000/stock/${code}?limit=60`)
    stockHistory.value = res.data.data
  } catch (error) {
    console.error('获取K线数据失败', error)
    alert('获取K线数据失败')
  }
}

// 初始化
fetchMomentum()
</script>

<style>
table { border-collapse: collapse; width: 100%; }
th, td { padding: 8px; text-align: center; }
</style>