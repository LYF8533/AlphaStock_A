<template>
  <div ref="chart" style="width: 100%; height: 400px;"></div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Array, default: () => [] }
})

const chart = ref(null)
let myChart = null

// 只在组件挂载时初始化一次
onMounted(() => {
  myChart = echarts.init(chart.value)
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)

  // 如果已经有数据，直接渲染
  if (props.data.length) {
    renderChart()
  }
})

// 组件销毁时释放资源
onUnmounted(() => {
  if (myChart) {
    myChart.dispose()
    myChart = null
  }
  window.removeEventListener('resize', handleResize)
})

const handleResize = () => {
  if (myChart) {
    myChart.resize()
  }
}

// 渲染图表
const renderChart = () => {
  if (!myChart || !props.data.length) return

  // 转换数据格式：日期从远到近
  const chartData = [...props.data].reverse()
  const dates = chartData.map(item => item.trade_date)
  const prices = chartData.map(item => item.close)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const data = params[0]
        return `${data.name}<br/>收盘价: ${data.data}`
      }
    },
    xAxis: {
      type: 'category',
      data: dates,
      name: '日期',
      axisLabel: { rotate: 30 }
    },
    yAxis: {
      type: 'value',
      name: '价格 (元)',
      scale: true
    },
    series: [{
      data: prices,
      type: 'line',
      name: '收盘价',
      smooth: true,
      lineStyle: { width: 2 },
      areaStyle: { opacity: 0.1 }
    }],
    grid: {
      left: '10%',
      right: '5%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    dataZoom: [
      { type: 'slider', start: 0, end: 100 },
      { type: 'inside', start: 0, end: 100 }
    ]
  }

  myChart.setOption(option)
}

// 监听数据变化
watch(() => props.data, () => {
  renderChart()
}, { deep: true })
</script>