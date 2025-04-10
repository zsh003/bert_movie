<template>
  <div class="movie-analytics">
    <h2>电影数据分析</h2>
    
    <a-row :gutter="[16, 16]">
      <a-col :span="12">
        <a-card title="电影类型分布">
          <div ref="genreChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="上映年份分布">
          <div ref="yearChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
      <a-col :span="24">
        <a-card title="电影评分分布">
          <div ref="ratingChartRef" style="height: 400px"></div>
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
import type { EChartsOption } from 'echarts';

export default defineComponent({
  name: 'MovieAnalytics',
  setup() {
    const genreChartRef = ref<HTMLElement>();
    const yearChartRef = ref<HTMLElement>();
    const ratingChartRef = ref<HTMLElement>();
    let genreChart: echarts.ECharts;
    let yearChart: echarts.ECharts;
    let ratingChart: echarts.ECharts;

    const initCharts = () => {
      if (genreChartRef.value) {
        genreChart = echarts.init(genreChartRef.value);
      }
      if (yearChartRef.value) {
        yearChart = echarts.init(yearChartRef.value);
      }
      if (ratingChartRef.value) {
        ratingChart = echarts.init(ratingChartRef.value);
      }
    };

    const fetchData = async () => {
      try {
        const response = await axios.get('/api/analytics/movies');
        const data = response.data;

        // 类型分布饼图
        const genreOption: EChartsOption = {
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          series: [
            {
              name: '电影类型',
              type: 'pie',
              radius: ['40%', '70%'],
              avoidLabelOverlap: false,
              itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
              },
              label: {
                show: true,
                position: 'outside'
              },
              data: data.genreDistribution
            }
          ]
        };
        genreChart.setOption(genreOption);

        // 年份分布柱状图
        const yearOption: EChartsOption = {
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            type: 'category',
            data: data.yearDistribution.map(item => item.name)
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: '电影数量',
              type: 'bar',
              data: data.yearDistribution.map(item => item.value)
            }
          ]
        };
        yearChart.setOption(yearOption);

        // 评分分布折线图
        const ratingOption: EChartsOption = {
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            type: 'category',
            data: data.ratingDistribution.map(item => item.name)
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: '电影数量',
              type: 'line',
              smooth: true,
              data: data.ratingDistribution.map(item => item.value)
            }
          ]
        };
        ratingChart.setOption(ratingOption);

      } catch (error) {
        message.error('获取数据失败');
      }
    };

    onMounted(() => {
      initCharts();
      fetchData();

      window.addEventListener('resize', () => {
        genreChart?.resize();
        yearChart?.resize();
        ratingChart?.resize();
      });
    });

    return {
      genreChartRef,
      yearChartRef,
      ratingChartRef
    };
  }
});
</script>

<style scoped>
.movie-analytics {
  padding: 24px;
}

h2 {
  margin-bottom: 24px;
}
</style> 