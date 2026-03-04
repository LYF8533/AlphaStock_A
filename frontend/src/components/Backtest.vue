<template>
  <div style="padding: 20px; background-color: #1e1e1e; min-height: 100vh; color: #e0e0e0;">
    <!-- 选股/回测切换导航（假设你的 App.vue 里有，这里只是占位） -->

    <h1 style="color: #ffffff;">动量策略回测</h1>

    <!-- 数据源提示 - 深色背景适配 -->
    <div v-if="dataSource" style="margin: 15px 0; padding: 12px 16px; background-color: #2d2d2d; border-radius: 6px; border-left: 6px solid #bb86fc; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
      <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 10px;">
        <span style="font-weight: bold; font-size: 1.1em; color: #ffffff;">📊 当前数据源：</span>
        <span style="font-size: 1.1em; color: #e0e0e0;">{{ dataSource }}</span>
        <span v-if="dataSource.includes('示例')" style="background-color: #4a2a2a; color: #ff8a80; padding: 4px 12px; border-radius: 20px; font-size: 0.9em; font-weight: bold; border: 1px solid #cf6679;">
          ⚠️ 数据库未连接（使用示例数据）
        </span>
        <span v-else style="background-color: #1e3a2e; color: #8bc34a; padding: 4px 12px; border-radius: 20px; font-size: 0.9em; font-weight: bold; border: 1px solid #4caf50;">
          ✅ 数据库连接正常
        </span>
      </div>
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
import { ref, nextTick } from 'vue'
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