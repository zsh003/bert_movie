<template>
  <div class="user-analytics">
    <h2>用户数据分析</h2>
    
    <a-row :gutter="[16, 16]">
      <a-col :span="12">
        <a-card title="用户活跃度">
          <div ref="activityChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="用户注册趋势">
          <div ref="registrationChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
      <a-col :span="24">
        <a-card title="用户行为分析">
          <div ref="behaviorChartRef" style="height: 400px"></div>
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
  name: 'UserAnalytics',
  setup() {
    const activityChartRef = ref<HTMLElement>();
    const registrationChartRef = ref<HTMLElement>();
    const behaviorChartRef = ref<HTMLElement>();
    let activityChart: echarts.ECharts;
    let registrationChart: echarts.ECharts;
    let behaviorChart: echarts.ECharts;

    const initCharts = () => {
      if (activityChartRef.value) {
        activityChart = echarts.init(activityChartRef.value);
      }
      if (registrationChartRef.value) {
        registrationChart = echarts.init(registrationChartRef.value);
      }
      if (behaviorChartRef.value) {
        behaviorChart = echarts.init(behaviorChartRef.value);
      }
    };

    const fetchData = async () => {
      try {
        const response = await axios.get('/api/analytics/users');
        const data = response.data;

        // 用户活跃度热力图
        const activityOption: EChartsOption = {
          tooltip: {
            position: 'top'
          },
          calendar: {
            top: 40,
            left: 30,
            right: 30,
            cellSize: ['auto', 20],
            range: data.activityRange,
            itemStyle: {
              borderWidth: 0.5
            }
          },
          visualMap: {
            min: 0,
            max: 10,
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            top: 0
          },
          series: [{
            type: 'heatmap',
            coordinateSystem: 'calendar',
            data: data.activityData
          }]
        };
        activityChart.setOption(activityOption);

        // 用户注册趋势折线图
        const registrationOption: EChartsOption = {
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            type: 'category',
            data: data.registrationTrend.map(item => item.date)
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: '新注册用户',
              type: 'line',
              smooth: true,
              data: data.registrationTrend.map(item => item.count)
            }
          ]
        };
        registrationChart.setOption(registrationOption);

        // 用户行为分析柱状图
        const behaviorOption: EChartsOption = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          legend: {
            data: ['评论', '收藏']
          },
          xAxis: {
            type: 'category',
            data: data.behaviorAnalysis.dates
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: '评论',
              type: 'bar',
              data: data.behaviorAnalysis.reviews
            },
            {
              name: '收藏',
              type: 'bar',
              data: data.behaviorAnalysis.favorites
            }
          ]
        };
        behaviorChart.setOption(behaviorOption);

      } catch (error) {
        message.error('获取数据失败');
      }
    };

    onMounted(() => {
      initCharts();
      fetchData();

      window.addEventListener('resize', () => {
        activityChart?.resize();
        registrationChart?.resize();
        behaviorChart?.resize();
      });
    });

    return {
      activityChartRef,
      registrationChartRef,
      behaviorChartRef
    };
  }
});
</script>

<style scoped>
.user-analytics {
  padding: 24px;
}

h2 {
  margin-bottom: 24px;
}
</style> 