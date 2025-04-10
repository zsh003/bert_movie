<template>
  <div class="movie-analytics">
    <a-page-header title="电影数据分析" />
    
    <a-row :gutter="[16, 16]">
      <a-col :span="12">
        <a-card title="评分分布">
          <div ref="ratingChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="类型分布">
          <div ref="genreChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
      <a-col :span="24">
        <a-card title="发布趋势">
          <div ref="trendChartRef" style="height: 400px"></div>
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
import type { EChartsOption } from 'echarts';

export default defineComponent({
  name: 'MovieAnalytics',
  setup() {
    const ratingChartRef = ref<HTMLElement>();
    const genreChartRef = ref<HTMLElement>();
    const trendChartRef = ref<HTMLElement>();
    let ratingChart: echarts.ECharts;
    let genreChart: echarts.ECharts;
    let trendChart: echarts.ECharts;

    const initCharts = () => {
      if (ratingChartRef.value) {
        ratingChart = echarts.init(ratingChartRef.value);
      }
      if (genreChartRef.value) {
        genreChart = echarts.init(genreChartRef.value);
      }
      if (trendChartRef.value) {
        trendChart = echarts.init(trendChartRef.value);
      }
    };

    const fetchData = async () => {
      try {
        const { data } = await axios.get('/api/analytics/movies');
        
        // 评分分布柱状图
        const ratingOption: EChartsOption = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          xAxis: {
            type: 'category',
            data: data.ratingDistribution.ratings.map((r: number) => `${r}分`),
            name: '评分'
          },
          yAxis: {
            type: 'value',
            name: '电影数量'
          },
          series: [
            {
              name: '电影数量',
              type: 'bar',
              data: data.ratingDistribution.counts,
              itemStyle: {
                color: '#5470c6'
              },
              label: {
                show: true,
                position: 'top'
              }
            }
          ]
        };
        ratingChart.setOption(ratingOption);

        // 类型分布饼图
        const genreOption: EChartsOption = {
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 'left',
            type: 'scroll'
          },
          series: [
            {
              name: '电影类型',
              type: 'pie',
              radius: ['40%', '70%'],
              avoidLabelOverlap: false,
              label: {
                show: true,
                position: 'outside',
                formatter: '{b}: {c}'
              },
              emphasis: {
                label: {
                  show: true,
                  fontSize: '16',
                  fontWeight: 'bold'
                }
              },
              data: data.genreDistribution.genres.map((genre: string, index: number) => ({
                name: genre,
                value: data.genreDistribution.counts[index]
              }))
            }
          ]
        };
        genreChart.setOption(genreOption);

        // 发布趋势折线图
        const trendOption: EChartsOption = {
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            type: 'category',
            data: data.releaseTrend.months,
            axisLabel: {
              rotate: 45
            }
          },
          yAxis: {
            type: 'value',
            name: '发布数量'
          },
          series: [
            {
              name: '发布数量',
              type: 'line',
              smooth: true,
              areaStyle: {
                opacity: 0.3
              },
              data: data.releaseTrend.counts,
              itemStyle: {
                color: '#91cc75'
              }
            }
          ]
        };
        trendChart.setOption(trendOption);

      } catch (error) {
        message.error('获取数据失败');
        console.error('Error fetching movie analytics:', error);
      }
    };

    const handleResize = () => {
      ratingChart?.resize();
      genreChart?.resize();
      trendChart?.resize();
    };

    onMounted(() => {
      initCharts();
      fetchData();
      window.addEventListener('resize', handleResize);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize);
      ratingChart?.dispose();
      genreChart?.dispose();
      trendChart?.dispose();
    });

    return {
      ratingChartRef,
      genreChartRef,
      trendChartRef
    };
  }
});
</script>

<style scoped>
.movie-analytics {
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