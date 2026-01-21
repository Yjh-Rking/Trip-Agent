<script setup lang="ts">
import { ref } from 'vue'
import { DatePicker, Input, Select, Button, Card, Spin, message, Alert, Typography, Row, Col, Descriptions, Divider, Tag } from 'ant-design-vue'
import { generateItinerary, type TravelRequest, type TripPlanResponse } from '../api'

const { TextArea } = Input
const { Paragraph, Title, Text } = Typography
const { Item: DescriptionsItem } = Descriptions

const loading = ref(false)
const responseData = ref<TripPlanResponse | null>(null)

const formState = ref<TravelRequest>({
  city: '',
  start_date: '',
  end_date: '',
  travel_days: 3,
  transportation: '火车',
  accommodation: '经济型',
  preferences: [],
  free_text_input: ''
})

const transportationOptions = [
  { value: '火车', label: '火车' },
  { value: '飞机', label: '飞机' },
  { value: '自驾', label: '自驾' },
  { value: '高铁', label: '高铁' },
  { value: '巴士', label: '巴士' },
  { value: '公共交通', label: '公共交通' }
]

const accommodationOptions = [
  { value: '经济型', label: '经济型' },
  { value: '舒适型', label: '舒适型' },
  { value: '豪华型', label: '豪华型' },
  { value: '民宿', label: '民宿' },
  { value: '青年旅舍', label: '青年旅舍' }
]

const preferenceOptions = [
  { value: '历史文化', label: '历史文化' },
  { value: '自然风光', label: '自然风光' },
  { value: '美食', label: '美食' },
  { value: '购物', label: '购物' },
  { value: '休闲度假', label: '休闲度假' },
  { value: '探险', label: '探险' },
  { value: '亲子', label: '亲子' },
  { value: '浪漫', label: '浪漫' }
]

const handleDateChange = () => {
  if (formState.value.start_date && formState.value.end_date) {
    const start = new Date(formState.value.start_date)
    const end = new Date(formState.value.end_date)
    const diffTime = Math.abs(end.getTime() - start.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
    formState.value.travel_days = diffDays > 0 ? diffDays : 1
  }
}

const handleSubmit = async () => {
  if (!formState.value.city) {
    message.warning('请输入目的地城市')
    return
  }
  if (!formState.value.start_date || !formState.value.end_date) {
    message.warning('请选择旅行日期')
    return
  }

  loading.value = true
  responseData.value = null

  try {
    const result = await generateItinerary(formState.value)
    responseData.value = result
    if (result.success) {
      message.success('行程生成成功！')
    } else {
      message.warning(result.message || '行程生成未成功')
    }
  } catch (error: any) {
    responseData.value = {
      success: false,
      message: '请求失败: ' + (error.response?.data?.message || error.message || '未知错误')
    }
    message.error('行程生成失败')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  formState.value = {
    city: '',
    start_date: '',
    end_date: '',
    travel_days: 3,
    transportation: '火车',
    accommodation: '经济型',
    preferences: [],
    free_text_input: ''
  }
  responseData.value = null
}
</script>

<template>
  <div class="container">
    <div class="header">
      <h1 class="title">Travel-Agent 智能旅行助手</h1>
      <p class="subtitle">基于AI的个性化旅行行程规划</p>
    </div>

    <Card class="form-card">
      <a-form :model="formState" layout="vertical">
        <a-row :gutter="24">
          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="目的地城市" required>
              <a-input
                v-model:value="formState.city"
                placeholder="请输入目的地，例如：北京"
                size="large"
              />
            </a-form-item>
          </a-col>

          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="开始日期" required>
              <a-date-picker
                v-model:value="formState.start_date"
                placeholder="选择开始日期"
                size="large"
                style="width: 100%"
                value-format="YYYY-MM-DD"
                @change="handleDateChange"
              />
            </a-form-item>
          </a-col>

          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="结束日期" required>
              <a-date-picker
                v-model:value="formState.end_date"
                placeholder="选择结束日期"
                size="large"
                style="width: 100%"
                value-format="YYYY-MM-DD"
                @change="handleDateChange"
              />
            </a-form-item>
          </a-col>

          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="旅行天数">
              <a-input-number
                v-model:value="formState.travel_days"
                :min="1"
                :max="30"
                size="large"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>

          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="交通方式">
              <a-select
                v-model:value="formState.transportation"
                placeholder="选择交通方式"
                size="large"
                :options="transportationOptions"
              />
            </a-form-item>
          </a-col>

          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="住宿偏好">
              <a-select
                v-model:value="formState.accommodation"
                placeholder="选择住宿偏好"
                size="large"
                :options="accommodationOptions"
              />
            </a-form-item>
          </a-col>

          <a-col :span="24">
            <a-form-item label="旅行偏好">
              <a-select
                v-model:value="formState.preferences"
                placeholder="选择旅行偏好（可多选）"
                size="large"
                mode="multiple"
                :options="preferenceOptions"
              />
            </a-form-item>
          </a-col>

          <a-col :span="24">
            <a-form-item label="额外要求">
              <TextArea
                v-model:value="formState.free_text_input"
                placeholder="请输入任何额外要求，例如：预算限制、特殊饮食需求、必去景点等"
                :rows="3"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item class="button-group">
          <a-space size="large">
            <a-button type="primary" size="large" @click="handleSubmit" :loading="loading">
              生成行程
            </a-button>
            <a-button size="large" @click="handleReset">
              重置
            </a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </Card>

    <Card v-if="responseData || loading" class="response-card">
      <template #title>
        <span>AI生成的旅行行程</span>
      </template>
      <template #extra>
        <a-tag v-if="loading" color="processing">
          <template #icon><Spin /></template>
          生成中...
        </a-tag>
        <a-tag v-else-if="responseData" :color="responseData.success ? 'green' : 'red'">
          {{ responseData.success ? '成功' : '失败' }}
        </a-tag>
      </template>
      <div class="response-content">
        <Spin v-if="loading">
          <div class="loading-placeholder">
            正在为您规划完美的旅行行程，请稍候...
          </div>
        </Spin>

        <template v-else-if="responseData">
          <a-alert
            v-if="!responseData.success"
            type="error"
            :message="responseData.message"
            show-icon
            style="margin-bottom: 16px"
          />

          <div v-if="responseData.data" class="trip-plan">
            <a-descriptions bordered :column="2" size="small">
              <a-descriptions-item label="目的地">
                {{ responseData.data.city }}
              </a-descriptions-item>
              <a-descriptions-item label="旅行时间">
                {{ responseData.data.start_date }} 至 {{ responseData.data.end_date }}
              </a-descriptions-item>
            </a-descriptions>

            <a-divider>每日行程</a-divider>

            <div v-for="day in responseData.data.days" :key="day.day_index" class="day-plan">
              <a-typography-title :level="4">第 {{ day.day_index }} 天 - {{ day.date }}</a-typography-title>
              <p class="day-description">{{ day.description }}</p>

              <a-row :gutter="16">
                <a-col :span="12">
                  <a-card title="景点" size="small" class="sub-card">
                    <div v-for="(attraction, idx) in day.attractions" :key="idx" class="item">
                      <a-typography-text strong>{{ attraction.name }}</a-typography-text>
                      <a-typography-text type="secondary"> - {{ attraction.visit_duration }}小时</a-typography-text>
                      <a-typography-text type="secondary" class="address">{{ attraction.address }}</a-typography-text>
                    </div>
                  </a-card>
                </a-col>
                <a-col :span="12">
                  <a-card title="餐饮" size="small" class="sub-card">
                    <div v-for="(meal, idx) in day.meals" :key="idx" class="item">
                      <a-tag :color="meal.type === 'breakfast' ? 'orange' : meal.type === 'lunch' ? 'green' : meal.type === 'dinner' ? 'blue' : 'purple'">
                        {{ meal.type === 'breakfast' ? '早餐' : meal.type === 'lunch' ? '午餐' : meal.type === 'dinner' ? '晚餐' : '小吃' }}
                      </a-tag>
                      <a-typography-text>{{ meal.name }}</a-typography-text>
                    </div>
                  </a-card>
                </a-col>
              </a-row>

              <a-card v-if="day.hotel" title="住宿" size="small" class="sub-card">
                <a-typography-text strong>{{ day.hotel.name }}</a-typography-text>
                <a-typography-text type="secondary"> | {{ day.hotel.price_range }} | 评分: {{ day.hotel.rating }}</a-typography-text>
                <a-typography-text type="secondary" class="address">{{ day.hotel.address }}</a-typography-text>
              </a-card>
            </div>

            <a-divider v-if="responseData.data.weather_info.length > 0">天气预报</a-divider>

            <a-row v-if="responseData.data.weather_info.length > 0" :gutter="16">
              <a-col v-for="weather in responseData.data.weather_info" :key="weather.date" :span="8">
                <a-card size="small" class="weather-card">
                  <a-typography-text strong>{{ weather.date }}</a-typography-text>
                  <p>{{ weather.day_weather }} / {{ weather.night_weather }}</p>
                  <p>{{ weather.day_temp }}°C / {{ weather.night_temp }}°C</p>
                  <a-typography-text type="secondary">{{ weather.wind_direction }} {{ weather.wind_power }}级</a-typography-text>
                </a-card>
              </a-col>
            </a-row>

            <a-divider>总体建议</a-divider>
            <a-typography-paragraph>
              {{ responseData.data.overall_suggestions }}
            </a-typography-paragraph>

            <a-card v-if="responseData.data.budget" title="预算概览" size="small" class="budget-card">
              <a-descriptions :column="5" size="small">
                <a-descriptions-item label="景点">{{ responseData.data.budget.total_attractions }}元</a-descriptions-item>
                <a-descriptions-item label="住宿">{{ responseData.data.budget.total_hotels }}元</a-descriptions-item>
                <a-descriptions-item label="餐饮">{{ responseData.data.budget.total_meals }}元</a-descriptions-item>
                <a-descriptions-item label="交通">{{ responseData.data.budget.total_transportation }}元</a-descriptions-item>
                <a-descriptions-item label="总计">
                  <a-typography-text strong>{{ responseData.data.budget.total }}元</a-typography-text>
                </a-descriptions-item>
              </a-descriptions>
            </a-card>
          </div>
        </template>
      </div>
    </Card>
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.title {
  font-size: 36px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 12px;
}

.subtitle {
  font-size: 18px;
  color: #666;
  margin: 0;
}

.form-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.button-group {
  margin-top: 24px;
  text-align: center;
}

.response-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.response-content {
  min-height: 100px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.loading-placeholder {
  text-align: center;
  color: #999;
  padding: 40px;
}

.trip-plan {
  padding: 16px;
}

.day-plan {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px dashed #e8e8e8;
}

.day-plan:last-child {
  border-bottom: none;
}

.day-description {
  color: #666;
  margin-bottom: 16px;
}

.sub-card {
  margin-bottom: 16px;
}

.item {
  margin-bottom: 8px;
}

.item:last-child {
  margin-bottom: 0;
}

.address {
  display: block;
  font-size: 12px;
  margin-top: 4px;
}

.weather-card {
  text-align: center;
  margin-bottom: 16px;
}

.weather-card p {
  margin: 4px 0;
}

.budget-card {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .title {
    font-size: 28px;
  }

  .subtitle {
    font-size: 14px;
  }

  .container {
    padding: 20px 12px;
  }
}
</style>
