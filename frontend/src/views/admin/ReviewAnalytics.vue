<template>
  <div class="review-analytics">
    <a-page-header title="影评数据分析" />
    
    <a-row :gutter="[16, 16]">
      <a-col :span="12">
        <a-card title="情感分布">
          <div ref="sentimentChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="评论数量趋势">
          <div ref="trendChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
      <a-col :span="24">
        <a-card title="热门关键词">
          <div ref="wordCloudRef" style="height: 400px"></div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onBeforeUnmount } from 'vue';
import { message } from 'ant-design-vue';
import axios from 'axios';
import * as echarts from 'echarts';
import 'echarts-wordcloud';
import type { EChartsOption } from 'echarts';

export default defineComponent({
  name: 'ReviewAnalytics',
  setup() {
    const sentimentChartRef = ref<HTMLElement>();
    const trendChartRef = ref<HTMLElement>();
    const wordCloudRef = ref<HTMLElement>();
    let sentimentChart: echarts.ECharts;
    let trendChart: echarts.ECharts;
    let wordCloudChart: echarts.ECharts;

    const initCharts = () => {
      if (sentimentChartRef.value) {
        sentimentChart = echarts.init(sentimentChartRef.value);
      }
      if (trendChartRef.value) {
        trendChart = echarts.init(trendChartRef.value);
      }
      if (wordCloudRef.value) {
        wordCloudChart = echarts.init(wordCloudRef.value);
      }
    };

    const fetchData = async () => {
      try {
        const { data } = await axios.get('/api/analytics/reviews');
        
        // 情感分布饼图
        const sentimentOption: EChartsOption = {
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 'left',
            data: ['积极', '中性', '消极']
          },
          series: [
            {
              name: '情感分布',
              type: 'pie',
              radius: ['50%', '70%'],
              avoidLabelOverlap: false,
              label: {
                show: true,
                position: 'outside',
                formatter: '{b}: {c} ({d}%)'
              },
              emphasis: {
                label: {
                  show: true,
                  fontSize: '16',
                  fontWeight: 'bold'
                }
              },
              data: [
                { value: data.sentimentDistribution.positive, name: '积极', itemStyle: { color: '#91cc75' } },
                { value: data.sentimentDistribution.neutral, name: '中性', itemStyle: { color: '#fac858' } },
                { value: data.sentimentDistribution.negative, name: '消极', itemStyle: { color: '#ee6666' } }
              ]
            }
          ]
        };
        sentimentChart.setOption(sentimentOption);

        // 评论数量趋势图
        const trendOption: EChartsOption = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          xAxis: {
            type: 'category',
            data: data.reviewTrend.dates,
            axisLabel: {
              rotate: 45
            }
          },
          yAxis: {
            type: 'value',
            name: '评论数量'
          },
          series: [
            {
              name: '评论数量',
              type: 'line',
              smooth: true,
              areaStyle: {
                opacity: 0.3
              },
              data: data.reviewTrend.counts,
              itemStyle: {
                color: '#73c0de'
              }
            }
          ]
        };
        trendChart.setOption(trendOption);

        // 关键词词云图
        const wordCloudOption: EChartsOption = {
          tooltip: {
            show: true
          },
          series: [{
            type: 'wordCloud',
            shape: 'circle',
            left: 'center',
            top: 'center',
            width: '80%',
            height: '80%',
            right: null,
            bottom: null,
            sizeRange: [12, 60],
            rotationRange: [-45, 45],
            rotationStep: 45,
            gridSize: 8,
            drawOutOfBound: false,
            textStyle: {
              fontFamily: 'sans-serif',
              fontWeight: 'bold',
              color: function () {
                return 'rgb(' + [
                  Math.round(Math.random() * 160),
                  Math.round(Math.random() * 160),
                  Math.round(Math.random() * 160)
                ].join(',') + ')';
              }
            },
            emphasis: {
              focus: 'self',
              textStyle: {
                shadowBlur: 10,
                shadowColor: '#333'
              }
            },
            data: data.keywords
          }]
        };
        wordCloudChart.setOption(wordCloudOption);

      } catch (error) {
        message.error('获取数据失败');
        console.error('Error fetching review analytics:', error);
      }
    };

    const handleResize = () => {
      sentimentChart?.resize();
      trendChart?.resize();
      wordCloudChart?.resize();
    };

    onMounted(() => {
      initCharts();
      fetchData();
      window.addEventListener('resize', handleResize);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize);
      sentimentChart?.dispose();
      trendChart?.dispose();
      wordCloudChart?.dispose();
    });

    return {
      sentimentChartRef,
      trendChartRef,
      wordCloudRef
    };
  }
});
</script>

<style scoped>
.review-analytics {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100vh;
}

:deep(.ant-card) {
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

:deep(.ant-card-head) {
  border-bottom: 1px solid #f0f0f0;
  padding: 0 24px;
}

:deep(.ant-card-head-title) {
  font-size: 16px;
  font-weight: 500;
}

:deep(.ant-page-header) {
  padding: 16px 0;
}
</style> 