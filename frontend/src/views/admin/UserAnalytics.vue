<template>
  <div class="user-analytics">
    <a-page-header title="用户数据分析" />
    
    <a-row :gutter="[16, 16]">
      <a-col :span="24">
        <a-card title="用户活跃度">
          <div ref="activityChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="用户注册趋势">
          <div ref="registrationChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="用户行为分析">
          <div ref="behaviorChartRef" style="height: 400px"></div>
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
        const { data } = await axios.get('/api/analytics/users');
        
        // 用户活跃度热力图
        const activityOption: EChartsOption = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          xAxis: {
            type: 'category',
            data: data.activityData.dates,
            axisLabel: {
              rotate: 45
            }
          },
          yAxis: {
            type: 'value',
            name: '活跃用户数'
          },
          series: [
            {
              name: '活跃用户',
              type: 'line',
              smooth: true,
              areaStyle: {
                opacity: 0.3
              },
              data: data.activityData.counts,
              itemStyle: {
                color: '#5470c6'
              },
              markPoint: {
                data: [
                  { type: 'max', name: '最大值' },
                  { type: 'min', name: '最小值' }
                ]
              }
            }
          ]
        };
        activityChart.setOption(activityOption);

        // 用户注册趋势图
        const registrationOption: EChartsOption = {
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            type: 'category',
            data: data.registrationTrend.months,
            axisLabel: {
              rotate: 45
            }
          },
          yAxis: {
            type: 'value',
            name: '注册用户数'
          },
          series: [
            {
              name: '注册用户',
              type: 'bar',
              data: data.registrationTrend.counts,
              itemStyle: {
                color: '#91cc75'
              },
              label: {
                show: true,
                position: 'top'
              }
            }
          ]
        };
        registrationChart.setOption(registrationOption);

        // 用户行为分析饼图
        const total = data.userBehaviors.totalUsers;
        const behaviorOption: EChartsOption = {
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 'left'
          },
          series: [
            {
              name: '用户行为',
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
              data: [
                {
                  name: '评论用户',
                  value: data.userBehaviors.reviews,
                  itemStyle: { color: '#5470c6' }
                },
                {
                  name: '收藏用户',
                  value: data.userBehaviors.favorites,
                  itemStyle: { color: '#91cc75' }
                },
                {
                  name: '其他用户',
                  value: total - data.userBehaviors.reviews - data.userBehaviors.favorites,
                  itemStyle: { color: '#fac858' }
                }
              ]
            }
          ]
        };
        behaviorChart.setOption(behaviorOption);

      } catch (error) {
        message.error('获取数据失败');
        console.error('Error fetching user analytics:', error);
      }
    };

    const handleResize = () => {
      activityChart?.resize();
      registrationChart?.resize();
      behaviorChart?.resize();
    };

    onMounted(() => {
      initCharts();
      fetchData();
      window.addEventListener('resize', handleResize);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize);
      activityChart?.dispose();
      registrationChart?.dispose();
      behaviorChart?.dispose();
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