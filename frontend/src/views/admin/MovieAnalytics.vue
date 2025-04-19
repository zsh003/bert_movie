<template>
  <div class="movie-analytics">
    <a-page-header title="电影数据分析" />
    
    <a-row :gutter="[16, 16]">
      <a-col :span="12">
        <a-card title="电影评分分布">
          <div ref="ratingChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="影评长度分布">
          <div ref="lengthChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
      <a-col :span="24">
        <a-card title="热门电影排行">
          <div ref="popularChartRef" style="height: 400px"></div>
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
import { useUserStore } from '../../stores/user'

export default defineComponent({
  name: 'MovieAnalytics',
  setup() {
    const userStore = useUserStore();
    const ratingChartRef = ref<HTMLElement>();
    const lengthChartRef = ref<HTMLElement>();
    const popularChartRef = ref<HTMLElement>();
    let ratingChart: echarts.ECharts;
    let lengthChart: echarts.ECharts;
    let popularChart: echarts.ECharts;

    const initCharts = () => {
      if (ratingChartRef.value) {
        ratingChart = echarts.init(ratingChartRef.value);
      }
      if (lengthChartRef.value) {
        lengthChart = echarts.init(lengthChartRef.value);
      }
      if (popularChartRef.value) {
        popularChart = echarts.init(popularChartRef.value);
      }
    };

    const fetchData = async () => {
      try {
        // 获取电影评分分布数据
        const ratingResponse = await axios.get('http://localhost:8000/api/analysis/movie-rating-distribution', {
          headers: {
            'Authorization': `Bearer ${userStore.token}`
          }
        });
        
        const ratingData = ratingResponse.data;
        const ratingOption: EChartsOption = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          xAxis: {
            type: 'category',
            data: ['1分', '2分', '3分', '4分', '5分'],
          },
          yAxis: {
            type: 'value',
            name: '数量'
          },
          series: [
            {
              name: '评分分布',
              type: 'bar',
              data: ratingData.ratings || [],
              itemStyle: {
                color: function(params) {
                  const colorList = ['#ee6666', '#fac858', '#91cc75', '#5470c6', '#73c0de'];
                  return colorList[params.dataIndex];
                }
              }
            }
          ]
        };
        ratingChart.setOption(ratingOption);

        // 获取评论长度分布数据
        const lengthResponse = await axios.get('http://localhost:8000/api/analysis/comment-length-distribution', {
          headers: {
            'Authorization': `Bearer ${userStore.token}`
          }
        });
        
        const lengthData = lengthResponse.data;
        const lengthOption: EChartsOption = {
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 'left',
            data: ['短评（<50字）', '中评（50-200字）', '长评（>200字）']
          },
          series: [
            {
              name: '评论长度',
              type: 'pie',
              radius: ['40%', '70%'],
              avoidLabelOverlap: false,
              label: {
                show: true,
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
                { value: lengthData.short || 0, name: '短评（<50字）', itemStyle: { color: '#5470c6' } },
                { value: lengthData.medium || 0, name: '中评（50-200字）', itemStyle: { color: '#91cc75' } },
                { value: lengthData.long || 0, name: '长评（>200字）', itemStyle: { color: '#fac858' } }
              ]
            }
          ]
        };
        lengthChart.setOption(lengthOption);

        // 获取用户活跃度数据作为热门电影排行的替代
        const userResponse = await axios.get('http://localhost:8000/api/analysis/user-activity', {
          headers: {
            'Authorization': `Bearer ${userStore.token}`
          }
        });
        
        const userData = userResponse.data;
        // 转换数据格式
        const movieNames = userData.map(item => item.movies && item.movies.length > 0 ? item.movies[0] : '未知电影').slice(0, 10);
        const reviewCounts = userData.map(item => item.review_count).slice(0, 10);
        
        const popularOption: EChartsOption = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          xAxis: {
            type: 'value',
            name: '评论数量'
          },
          yAxis: {
            type: 'category',
            data: movieNames,
            axisLabel: {
              width: 100,
              overflow: 'truncate'
            }
          },
          series: [
            {
              name: '评论数量',
              type: 'bar',
              data: reviewCounts,
              itemStyle: {
                color: '#73c0de'
              }
            }
          ]
        };
        popularChart.setOption(popularOption);

      } catch (error) {
        message.error('获取数据失败');
        console.error('Error fetching movie analytics:', error);
      }
    };

    const handleResize = () => {
      ratingChart?.resize();
      lengthChart?.resize();
      popularChart?.resize();
    };

    onMounted(() => {
      initCharts();
      fetchData();
      window.addEventListener('resize', handleResize);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize);
      ratingChart?.dispose();
      lengthChart?.dispose();
      popularChart?.dispose();
    });

    return {
      ratingChartRef,
      lengthChartRef,
      popularChartRef
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