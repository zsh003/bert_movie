<template>
  <div class="review-analytics">
    <h2>影评数据分析</h2>
    
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
import { defineComponent, ref, onMounted } from 'vue';
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
        const response = await axios.get('/api/analytics/reviews');
        const data = response.data;

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
                position: 'outside'
              },
              emphasis: {
                label: {
                  show: true,
                  fontSize: '16',
                  fontWeight: 'bold'
                }
              },
              data: [
                { value: data.sentimentDistribution.positive, name: '积极' },
                { value: data.sentimentDistribution.neutral, name: '中性' },
                { value: data.sentimentDistribution.negative, name: '消极' }
              ]
            }
          ]
        };
        sentimentChart.setOption(sentimentOption);

        // 评论数量趋势图
        const trendOption: EChartsOption = {
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            type: 'category',
            data: data.reviewTrend.dates
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: '评论数量',
              type: 'line',
              smooth: true,
              areaStyle: {},
              data: data.reviewTrend.counts
            }
          ]
        };
        trendChart.setOption(trendOption);

        // 关键词词云图
        const wordCloudOption: EChartsOption = {
          tooltip: {},
          series: [{
            type: 'wordCloud',
            shape: 'circle',
            left: 'center',
            top: 'center',
            width: '70%',
            height: '80%',
            right: null,
            bottom: null,
            sizeRange: [12, 60],
            rotationRange: [-90, 90],
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
            data: data.keywords.map(item => ({
              name: item.word,
              value: item.weight,
              textStyle: {
                color: null
              }
            }))
          }]
        };
        wordCloudChart.setOption(wordCloudOption);

      } catch (error) {
        message.error('获取数据失败');
      }
    };

    onMounted(() => {
      initCharts();
      fetchData();

      window.addEventListener('resize', () => {
        sentimentChart?.resize();
        trendChart?.resize();
        wordCloudChart?.resize();
      });
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
}

h2 {
  margin-bottom: 24px;
}
</style> 