<template>
  <div style="padding: 20px">
    <h1>动量策略回测</h1>
    <div style="margin: 20px 0;">
      <label>动量天数：</label><input v-model.number="lookback" type="number" min="5" max="120"> 日<br>
      <label>选股数量：</label><input v-model.number="topN" type="number" min="1" max="50"><br>
      <label>调仓频率：</label>
      <select v-model="freq">
        <option value="ME">月末</option>
        <option value="W">每周</option>
        <option value="D">每日</option>
      </select><br>
      <label>交易成本：</label><input v-model.number="cost" type="number" step="0.001" min="0" max="0.01"> (双边)<br>
      <button @click="runBacktest">运行回测</button>
    </div>

    <div v-if="loading">加载中...</div>

    <!-- 用 v-show 保证 chartNav 始终在 DOM 中 -->
    <div v-show="navData.length">
      <h2>净值曲线</h2>
      <div ref="chartNav" style="width: 100%; height: 400px;"></div>
      <h2>绩效指标</h2>
      <table border="1" style="width:100%; border-collapse: collapse;">
        <tr v-for="(value, key) in metrics" :key="key">
          <td style="padding:8px; font-weight:bold">{{ key }}</td>
          <td style="padding:8px">{{ value }}</td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const lookback = ref(30)
const topN = ref(20)
const freq = ref('ME')
const cost = ref(0.0025)
const loading = ref(false)
const navData = ref([])
const metrics = ref({})
const chartNav = ref(null)

const renderChart = () => {
  nextTick(() => {
    if (!chartNav.value) {
      console.error('chartNav 元素不存在，等待重试...')
      setTimeout(renderChart, 100) // 100ms 后重试
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
    // 延迟一点点，确保 DOM 更新
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