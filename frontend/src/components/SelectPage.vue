<template>
  <div style="padding: 20px">
    <!-- 数据源提示 -->
    <div v-if="dataSource" style="margin-bottom: 15px; padding: 8px 12px; background-color: #2d2d2d; border-radius: 4px; border-left: 4px solid #bb86fc;">
      <span style="font-weight: bold; color: #ffffff;">📊 当前数据源：</span>
      <span style="color: #e0e0e0;">{{ dataSource }}</span>
      <span v-if="dataSource.includes('示例')" style="margin-left: 10px; background-color: #4a2a2a; color: #ff8a80; padding: 2px 8px; border-radius: 12px; font-size: 0.9em;">
        ⚠️ 数据库未连接，使用示例数据
      </span>
      <span v-else style="margin-left: 10px; background-color: #1e3a2e; color: #8bc34a; padding: 2px 8px; border-radius: 12px; font-size: 0.9em;">
        ✅ 数据库连接正常
      </span>
    </div>

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

    <!-- K线图区域（带加载状态） -->
    <div v-if="selectedCode" style="margin-top: 30px;">
      <h2>{{ selectedCode }} K线图</h2>
      <div v-if="loadingKline" style="text-align: center; padding: 50px;">
        ⏳ K线加载中...
      </div>
      <div v-else>
        <StockChart :data="stockHistory" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref , onMounted } from 'vue'
import axios from 'axios'
import StockChart from './StockChart.vue'

const topN = ref(10)
const days = ref(20)
const topStocks = ref([])
const selectedCode = ref('000001')
const stockHistory = ref([])
const dataSource = ref('')
const dbStatus = ref(null)
const loadingKline = ref(false)

onMounted(async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/check_db')
    dbStatus.value = res.data.db_available
    dataSource.value = res.data.message
  }catch (error){
    dbStatus.value = false
    dataSource.value = '检测失败，使用示例数据'
  }
})

const fetchData = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/select/momentum', {
      params: { top_n: topN.value, days: days.value }
    })
    stockData.value = res.data.top
    if (res.data.data_source) {
      dataSource.value = res.data.data_source  // 后端返回的数据源
    }
  } catch (error) {
    console.error('选股失败', error)
    alert('选股接口调用失败')
  }
}

const fetchMomentum = async () => {
  console.log('开始请求选股数据')
  try {
    const res = await axios.get('http://127.0.0.1:8000/select/momentum', {
      params: { top_n: topN.value, days: days.value }
    })
    console.log('请求成功', res.data)
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
  loadingKline.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:8000/stock/${code}?limit=60`)
    stockHistory.value = res.data.data
  } catch (error) {
    console.error('获取K线数据失败', error)
    alert('获取K线数据失败')
  } finally {
    loadingKline.value = false
  }
}

// 初始化
fetchMomentum()
</script>

<style>
table { border-collapse: collapse; width: 100%; }
th, td { padding: 8px; text-align: center; }
</style>