<template>
  <div style="padding: 20px; background-color: #1e1e1e; min-height: 100vh; color: #e0e0e0;">
    <!-- 选股/回测切换导航（假设你的 App.vue 里有，这里只是占位） -->

    <h1 style="color: #ffffff;">动量策略回测</h1>

    <!-- 数据源提示 - 深色背景适配 -->
    <div v-if="dbStatus !== null"
     :style="{
       padding: '12px 16px',
       marginBottom: '20px',
       borderRadius: '6px',
       backgroundColor: dbStatus ? '#e8f5e8' : '#ffebee',
       color: dbStatus ? '#2e7d32' : '#c62828',
       border: dbStatus ? '1px solid #2e7d32' : '1px solid #c62828',
       fontSize: '15px'
     }">
  <span style="fontWeight: 'bold'">📊 当前数据源：</span> {{ dbMessage }}
  <span v-if="!dbStatus" style="marginLeft: '12px'; backgroundColor: 'rgba(198,40,40,0.1)'; padding: '4px 8px'; borderRadius: '4px'">
    ⚠️ 将使用示例数据（CSV）
  </span>
  <span v-else style="marginLeft: '12px'; backgroundColor: 'rgba(46,125,50,0.1)'; padding: '4px 8px'; borderRadius: '4px'">
    ✅ 数据库连接正常
  </span>
</div>

    <!-- 回测参数表单 - 深色背景 -->
    <div style="margin: 20px 0; padding: 15px; background-color: #2d2d2d; border-radius: 6px; border: 1px solid #3d3d3d;">
      <div style="margin-bottom: 10px;">
        <label style="display: inline-block; width: 80px; color: #e0e0e0;">动量天数：</label>
        <input v-model.number="lookback" type="number" min="5" max="120" style="width: 80px; background-color: #3d3d3d; color: #e0e0e0; border: 1px solid #4d4d4d; border-radius: 4px; padding: 4px;"> 日
      </div>
      <div style="margin-bottom: 10px;">
        <label style="display: inline-block; width: 80px; color: #e0e0e0;">选股数量：</label>
        <input v-model.number="topN" type="number" min="1" max="50" style="width: 80px; background-color: #3d3d3d; color: #e0e0e0; border: 1px solid #4d4d4d; border-radius: 4px; padding: 4px;">
      </div>
      <div style="margin-bottom: 10px;">
        <label style="display: inline-block; width: 80px; color: #e0e0e0;">调仓频率：</label>
        <select v-model="freq" style="width: 100px; background-color: #3d3d3d; color: #e0e0e0; border: 1px solid #4d4d4d; border-radius: 4px; padding: 4px;">
          <option value="ME">月末</option>
          <option value="W">每周</option>
          <option value="D">每日</option>
        </select>
      </div>
      <div style="margin-bottom: 15px;">
        <label style="display: inline-block; width: 80px; color: #e0e0e0;">交易成本：</label>
        <input v-model.number="cost" type="number" step="0.001" min="0" max="0.01" style="width: 80px; background-color: #3d3d3d; color: #e0e0e0; border: 1px solid #4d4d4d; border-radius: 4px; padding: 4px;"> (双边)
      </div>
      <button @click="runBacktest" style="padding: 8px 20px; background-color: #bb86fc; color: #000000; border: none; border-radius: 4px; cursor: pointer; font-size: 1em; font-weight: bold;">运行回测</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" style="margin: 20px 0; color: #888;">⏳ 加载中...</div>

    <!-- 回测结果展示 - 深色背景 -->
    <div v-if="navData.length" style="margin-top: 30px;">
      <h2 style="color: #ffffff;">净值曲线</h2>
      <div ref="chartNav" style="width: 100%; height: 400px; border: 1px solid #3d3d3d; border-radius: 4px; background-color: #2d2d2d;"></div>

      <h2 style="margin-top: 30px; color: #ffffff;">绩效指标</h2>
      <table style="width: 100%; border-collapse: collapse; border: 1px solid #3d3d3d; background-color: #2d2d2d;">
        <tr v-for="(value, key) in metrics" :key="key" style="border-bottom: 1px solid #3d3d3d;">
          <td style="padding: 10px; font-weight: bold; background-color: #1e1e1e; width: 150px; color: #e0e0e0;">{{ key }}</td>
          <td style="padding: 10px; color: #e0e0e0;">{{ value }}</td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const dataSource = ref('')
const lookback = ref(30)
const topN = ref(20)
const freq = ref('ME')
const cost = ref(0.0025)
const loading = ref(false)
const navData = ref([])
const metrics = ref({})
const chartNav = ref(null)
// 新增：检测数据库状态
const dbStatus = ref(null)        // null: 加载中, true: 可用, false: 不可用
const dbMessage = ref('')

const checkDbStatus = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/check_db')
    dbStatus.value = res.data.db_available
    dbMessage.value = res.data.message
    console.log('数据库状态:', res.data)
  } catch (error) {
    console.error('检测数据库失败', error)
    dbStatus.value = false
    dbMessage.value = '检测失败，使用示例数据'
  }
}

// 页面加载时调用
onMounted(() => {
  checkDbStatus()
})
const renderChart = () => {
  nextTick(() => {
    if (!chartNav.value) {
      console.error('chartNav 元素不存在，等待重试...')
      setTimeout(renderChart, 100)
      return
    }
    try {
      const chart = echarts.init(chartNav.value)
      const dates = navData.value.map(item => item.date)
      const values = navData.value.map(item => item.value)
      chart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: dates },
        yAxis: { type: 'value' },
        series: [{ data: values, type: 'line', name: '策略净值' }]
      })
    } catch (error) {
      console.error('ECharts 初始化失败:', error)
    }
  })
}

const runBacktest = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://127.0.0.1:8000/backtest', {
      params: {
        lookback: lookback.value,
        top_n: topN.value,
        rebalance_freq: freq.value,
        cost: cost.value
      }
    })
    navData.value = res.data.nav
    metrics.value = res.data.metrics
    dataSource.value = res.data.data_source

    setTimeout(() => {
      renderChart()
    }, 50)
  } catch (error) {
    console.error('回测失败', error)
    alert('回测接口调用失败')
  } finally {
    loading.value = false
  }
}
</script>