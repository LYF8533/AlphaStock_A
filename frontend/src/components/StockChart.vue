<template>
  <div ref="chart" style="width: 100%; height: 400px;"></div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: { type: Array, default: () => [] }
})

const chart = ref(null)
let myChart = null

const renderChart = () => {
  if (!myChart) {
    myChart = echarts.init(chart.value)
  }

  if (!props.data.length) {
    myChart.clear()
    return
  }

  // 构建K线数据（日期从远到近）
  const kData = props.data.map(item => ({
    date: item.trade_date,
    open: item.open,
    close: item.close,
    low: item.low,
    high: item.high
  })).reverse()

  const dates = kData.map(d => d.date)
  const values = kData.map(d => [d.open, d.close, d.low, d.high])  // [open, close, low, high]

  const option = {
    title: { text: 'K线图', left: 'center' },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: function(params) {
        const idx = params[0].dataIndex
        const item = kData[idx]
        return `${item.date}\n开盘: ${item.open}\n收盘: ${item.close}\n最低: ${item.low}\n最高: ${item.high}`
      }
    },
    xAxis: {
      type: 'category',
      data: dates,
      name: '日期',
      nameLocation: 'middle',
      nameGap: 25
    },
    yAxis: {
      type: 'value',
      name: '价格 (元)',
      nameLocation: 'middle',
      nameGap: 35,
      scale: true
    },
    dataZoom: [
      { type: 'slider', start: 0, end: 100 },
      { type: 'inside', start: 0, end: 100 }
    ],
    series: [{
      name: 'K线',
      type: 'candlestick',
      data: values,
      itemStyle: {
        color: '#ef232a',      // 阳线（收盘>开盘）红色
        color0: '#14b143',     // 阴线（收盘<开盘）绿色
        borderColor: '#ef232a',
        borderColor0: '#14b143'
      }
    }]
  }
  myChart.setOption(option)
}

watch(() => props.data, () => {
  nextTick(() => { renderChart() })
}, { deep: true })

onMounted(() => {
  if (props.data.length) renderChart()
  window.addEventListener('resize', () => myChart?.resize())
})
</script>